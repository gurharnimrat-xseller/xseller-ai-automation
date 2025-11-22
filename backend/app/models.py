from __future__ import annotations

# from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, JSON, func, Integer
from sqlmodel import Field, SQLModel

try:
    from werkzeug.security import check_password_hash, generate_password_hash
except ImportError:
    # Fallback minimal implementations if werkzeug isn't available
    import hashlib

    def generate_password_hash(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def check_password_hash(pwhash: str, password: str) -> bool:
        return pwhash == hashlib.sha256(password.encode("utf-8")).hexdigest()


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    role: str = Field(default="admin", index=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    def set_password(self, password: str) -> None:
        """Set password hash from plain text password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if provided password matches the hash."""
        return check_password_hash(self.password_hash, password)


class Post(SQLModel, table=True):
    __tablename__ = "posts"

    id: Optional[int] = Field(default=None, primary_key=True)
    kind: str = Field(index=True)  # text or video
    title: str
    body: str
    source_url: Optional[str] = None
    content_hash: Optional[str] = Field(default=None, index=True)
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    platforms: Optional[List[str]] = Field(
        default=None, sa_column=Column(JSON))
    # draft, approved, published
    status: str = Field(default="draft", index=True)
    scheduled_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    published_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        ),
    )
    deleted_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    
    # Additional fields for content management
    hook_type: Optional[str] = Field(default=None, index=True)  # Type of viral hook used
    video_duration: Optional[int] = Field(default=None)  # Duration in seconds for video posts
    regeneration_count: int = Field(default=0, sa_column=Column(Integer))  # Number of times regenerated
    total_cost: Optional[float] = Field(default=None)  # Total cost of regeneration
    extra_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # Extra data for voice selection, etc.

    # Relationships (commented out for now due to SQLModel version compatibility)
    # assets: List["Asset"] = Relationship(back_populates="post")
    # publish_logs: List["PublishLog"] = Relationship(back_populates="post")
    # learning_logs: List["LearningLog"] = Relationship(back_populates="post")


class Asset(SQLModel, table=True):
    __tablename__ = "assets"

    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="posts.id", index=True)
    type: str = Field(index=True)  # video or image
    path: str
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    # post: Optional["Post"] = Relationship(back_populates="assets")


class PublishLog(SQLModel, table=True):
    __tablename__ = "publish_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="posts.id", index=True)
    provider: str = Field(index=True)  # publer, buffer, native
    platform: str = Field(index=True)  # youtube, tiktok, linkedin, x
    # success, failed, pending_retry
    status: str = Field(default="pending_retry", index=True)
    external_id: Optional[str] = Field(default=None, index=True)
    external_url: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = Field(default=0, sa_column=Column(Integer))
    next_retry_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    # post: Optional["Post"] = Relationship(back_populates="publish_logs")


class LearningLog(SQLModel, table=True):
    __tablename__ = "learning_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="posts.id", index=True)
    topic: str = Field(index=True)
    hook_type: Optional[str] = Field(default=None, index=True)
    metric_snapshot: Optional[dict] = Field(
        default=None, sa_column=Column(JSON))
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    # post: Optional["Post"] = Relationship(back_populates="learning_logs")


# ==================== News Ingestion Models (M01A) ====================


class Article(SQLModel, table=True):
    """News article from external sources."""
    __tablename__ = "articles"

    id: Optional[int] = Field(default=None, primary_key=True)
    source_name: str = Field(index=True)  # newsapi, mock, etc.
    external_id: str = Field(index=True, unique=True)  # Unique ID from source
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    published_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    fetched_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    # pending, ranked, scripted, published, rejected
    status: str = Field(default="pending", index=True)
    
    # Test mode fields for weekend testing
    is_test: bool = Field(default=False)
    test_batch_id: Optional[str] = Field(default=None)

    # Media production fields
    script: Optional[str] = None
    voice_url: Optional[str] = None
    broll_video_url: Optional[str] = None


class RankingScore(SQLModel, table=True):
    """AI ranking scores for articles."""
    __tablename__ = "ranking_scores"

    id: Optional[int] = Field(default=None, primary_key=True)
    article_id: int = Field(foreign_key="articles.id", index=True)
    score: float = Field(ge=0.0, le=1.0)  # Viral potential score 0-1
    reasoning: Optional[str] = None  # Why this score
    category: Optional[str] = Field(default=None, index=True)  # tech, business, etc.
    model_used: str = Field(default="gemini-1.5-flash")
    ranked_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )


class IngestionJob(SQLModel, table=True):
    """Track ingestion runs."""
    __tablename__ = "ingestion_jobs"

    id: Optional[int] = Field(default=None, primary_key=True)
    started_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    completed_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    # running, completed, failed, partial_failure
    status: str = Field(default="running", index=True)
    articles_fetched: int = Field(default=0, sa_column=Column(Integer))
    articles_ranked: int = Field(default=0, sa_column=Column(Integer))
    article_ids: Optional[List[int]] = Field(default=None, sa_column=Column(JSON))
    errors: Optional[dict] = Field(default=None, sa_column=Column(JSON))
