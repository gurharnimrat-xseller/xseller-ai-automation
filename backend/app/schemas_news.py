"""
Pydantic schemas for News API (M01A).

These schemas validate request/response data for the news ingestion and ranking pipeline.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


# ==================== Article Schemas ====================


class ArticleBase(BaseModel):
    """Base article fields."""
    source_name: str
    external_id: str
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    published_at: datetime


class ArticleCreate(ArticleBase):
    """Schema for creating an article."""
    pass


class ArticleResponse(ArticleBase):
    """Article response with database fields."""
    id: int
    status: str
    fetched_at: datetime

    class Config:
        from_attributes = True


# ==================== Ranking Schemas ====================


class RankingScoreResponse(BaseModel):
    """Ranking score response."""
    id: int
    article_id: int
    score: float
    reasoning: Optional[str] = None
    category: Optional[str] = None
    model_used: str
    ranked_at: datetime

    class Config:
        from_attributes = True


class ArticleWithScore(BaseModel):
    """Article with its latest ranking score."""
    article: ArticleResponse
    score: Optional[RankingScoreResponse] = None

    class Config:
        from_attributes = True


# ==================== Ingestion Schemas ====================


class IngestRequest(BaseModel):
    """Request to trigger news ingestion."""
    sources: List[str] = Field(
        default=["newsapi"],
        description="List of news sources to ingest from (newsapi, mock)"
    )
    limit_per_source: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Max articles to fetch per source"
    )

    @validator('sources')
    def validate_sources(cls, v):
        allowed = {'newsapi', 'mock'}
        invalid = set(v) - allowed
        if invalid:
            raise ValueError(f"Invalid sources: {invalid}. Allowed: {allowed}")
        return v


class IngestResponse(BaseModel):
    """Response from ingestion job."""
    job_id: int
    status: str
    started_at: datetime
    articles_fetched: int
    message: str


# ==================== Ranking Schemas ====================


class RankRequest(BaseModel):
    """Request to rank articles."""
    article_ids: List[int] = Field(
        description="List of article IDs to rank"
    )
    force_rerank: bool = Field(
        default=False,
        description="Force re-ranking even if already ranked"
    )

    @validator('article_ids')
    def validate_article_ids(cls, v):
        if not v:
            raise ValueError("article_ids cannot be empty")
        if len(v) > 50:
            raise ValueError("Cannot rank more than 50 articles at once")
        return v


class RankResponse(BaseModel):
    """Response from ranking operation."""
    ranked_count: int
    skipped_count: int
    scores: List[RankingScoreResponse]
    errors: Optional[List[str]] = None
