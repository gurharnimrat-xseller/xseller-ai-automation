"""
Test suite for M01A: News Ingestion + Ranking Pipeline

Tests the news ingestion and ranking functionality using mock data.
"""
from agents.checks.router import should_offload, offload_to_gemini  # guardrails

import pytest
from datetime import datetime, timezone
from sqlmodel import Session, create_engine, SQLModel
from app.models import Article, RankingScore, IngestionJob
from app.news_sources import MockNewsClient
from app.service_news_ingest import NewsIngestService
from app.service_news_ranking import NewsRankingService


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """Create a fresh test database for each test."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_mock_news_client():
    """Test that MockNewsClient returns expected number of articles."""
    client = MockNewsClient()
    articles = client.fetch_top_headlines(limit=5)

    assert len(articles) == 5
    assert all(hasattr(a, "source_name") for a in articles)
    assert all(hasattr(a, "title") for a in articles)
    assert all(hasattr(a, "url") for a in articles)


def test_ingest_service_stores_articles(session: Session):
    """Test that NewsIngestService correctly stores articles in database."""
    service = NewsIngestService(session)

    # Run ingestion with mock source
    job = service.run_ingestion(sources=["mock"], limit_per_source=5)

    # Check job was created
    assert job.id is not None
    assert job.status == "completed"
    assert job.articles_fetched == 5

    # Check articles were stored
    articles = session.query(Article).all()
    assert len(articles) == 5
    assert all(a.status == "pending" for a in articles)


def test_ingest_service_handles_duplicates(session: Session):
    """Test that duplicate articles (same external_id) are not inserted twice."""
    service = NewsIngestService(session)

    # First ingestion
    job1 = service.run_ingestion(sources=["mock"], limit_per_source=5)
    assert job1.articles_fetched == 5

    # Second ingestion (should find duplicates)
    job2 = service.run_ingestion(sources=["mock"], limit_per_source=5)
    assert job2.articles_fetched == 5

    # Should still only have 5 articles (no duplicates)
    articles = session.query(Article).all()
    assert len(articles) == 5


def test_get_pending_articles(session: Session):
    """Test retrieving pending articles."""
    service = NewsIngestService(session)

    # Ingest some articles
    service.run_ingestion(sources=["mock"], limit_per_source=5)

    # Get pending articles
    pending = service.get_pending_articles(limit=10)
    assert len(pending) == 5
    assert all(a.status == "pending" for a in pending)


def test_ranking_service_creates_scores(session: Session):
    """Test that NewsRankingService creates ranking scores for articles.

    Note: This test may fail if the GEMINI_API_KEY is not set or if the API call fails.
    In CI, ensure GEMINI_API_KEY is available as a secret.
    """
    # First ingest articles
    ingest_service = NewsIngestService(session)
    ingest_service.run_ingestion(sources=["mock"], limit_per_source=2)

    # Get article IDs
    articles = session.query(Article).all()
    article_ids = [a.id for a in articles if a.id is not None]

    # Rank articles
    ranking_service = NewsRankingService(session)
    scores = ranking_service.rank_articles(article_ids, force_rerank=False)

    # Check scores were created
    assert len(scores) == len(article_ids)
    for article_id, score in scores.items():
        assert 0.0 <= score.score <= 1.0
        assert score.model_used is not None
        assert score.reasoning is not None


def test_ranking_service_skips_already_ranked(session: Session):
    """Test that ranking service skips already-ranked articles unless force_rerank=True."""
    # First ingest and rank
    ingest_service = NewsIngestService(session)
    ingest_service.run_ingestion(sources=["mock"], limit_per_source=2)

    articles = session.query(Article).all()
    article_ids = [a.id for a in articles if a.id is not None]

    ranking_service = NewsRankingService(session)

    # First ranking
    scores1 = ranking_service.rank_articles(article_ids, force_rerank=False)
    assert len(scores1) == len(article_ids)

    # Second ranking without force (should skip)
    scores2 = ranking_service.rank_articles(article_ids, force_rerank=False)
    assert len(scores2) == 0  # All already ranked

    # Third ranking with force (should re-rank)
    scores3 = ranking_service.rank_articles(article_ids, force_rerank=True)
    assert len(scores3) == len(article_ids)


def test_get_top_ranked_articles(session: Session):
    """Test retrieving top-ranked articles."""
    # Ingest and rank articles
    ingest_service = NewsIngestService(session)
    ingest_service.run_ingestion(sources=["mock"], limit_per_source=3)

    articles = session.query(Article).all()
    article_ids = [a.id for a in articles if a.id is not None]

    ranking_service = NewsRankingService(session)
    ranking_service.rank_articles(article_ids, force_rerank=False)

    # Get top ranked (min_score=0.0 to include all)
    top_articles = ranking_service.get_top_ranked_articles(limit=10, min_score=0.0)

    assert len(top_articles) > 0
    # Check articles are sorted by score (descending)
    scores = [a[1].score for a in top_articles]
    assert scores == sorted(scores, reverse=True)
