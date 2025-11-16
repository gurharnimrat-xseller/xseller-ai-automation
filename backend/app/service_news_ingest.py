"""
News ingestion service (M01A).

Handles fetching articles from external sources and storing them in the database.
"""
from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401 guardrails

import os
from datetime import datetime
from typing import List
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from .models import Article, IngestionJob
from .news_sources import get_news_client, NewsArticleRaw


class NewsIngestService:
    """Service for ingesting news articles from external sources."""

    def __init__(self, db: Session):
        self.db = db
        self.news_api_key = os.getenv("NEWS_API_KEY", "")

    def run_ingestion(
        self,
        sources: List[str],
        limit_per_source: int = 10
    ) -> tuple[IngestionJob, List[int]]:
        """
        Run a news ingestion job from specified sources.

        Args:
            sources: List of source names to ingest from
            limit_per_source: Max articles to fetch per source

        Returns:
            Tuple of (IngestionJob record with results, list of article IDs)
        """
        # Create job record
        job = IngestionJob(
            status="running",
            articles_fetched=0,
            articles_ranked=0,
            errors={}
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        total_fetched = 0
        errors = {}
        article_ids = []

        # Process each source
        for source_name in sources:
            try:
                # Get client
                client = get_news_client(
                    source_name=source_name,
                    api_key=self.news_api_key if source_name == "newsapi" else None
                )

                # Fetch articles (with timeout handled by client)
                raw_articles = client.fetch_top_headlines(limit=limit_per_source)

                # Store articles and collect IDs
                stored_count, new_ids = self._store_articles(raw_articles)
                total_fetched += stored_count
                article_ids.extend(new_ids)

            except Exception as e:
                errors[source_name] = str(e)
                print(f"[Ingest] Error from {source_name}: {e}")

        # Update job status
        job.articles_fetched = total_fetched
        job.completed_at = datetime.utcnow()

        if errors:
            job.status = "partial_failure" if total_fetched > 0 else "failed"
            job.errors = errors
        else:
            job.status = "completed"

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        return job, article_ids

    def _store_articles(self, raw_articles: List[NewsArticleRaw]) -> tuple[int, List[int]]:
        """
        Store raw articles in database, handling duplicates.

        Args:
            raw_articles: List of raw articles from source

        Returns:
            Tuple of (count of successfully stored articles, list of article IDs)
        """
        stored_count = 0
        article_ids = []
        articles_to_add = []

        # First pass: check for duplicates and prepare articles
        for raw in raw_articles:
            try:
                # Check if article already exists
                stmt = select(Article).where(Article.external_id == raw.external_id)
                existing = self.db.exec(stmt).first()

                if existing:
                    print(f"[Ingest] Skipping duplicate: {raw.external_id}")
                    # Still include existing article ID for downstream processing
                    article_ids.append(existing.id)
                    continue

                # Create new article (don't add to DB yet)
                article = Article(
                    source_name=raw.source_name,
                    external_id=raw.external_id,
                    title=raw.title,
                    description=raw.description,
                    content=raw.content,
                    url=raw.url,
                    image_url=raw.image_url,
                    published_at=raw.published_at,
                    status="pending"
                )
                articles_to_add.append(article)

            except Exception as e:
                print(f"[Ingest] Error preparing article {raw.external_id}: {e}")
                continue

        # Second pass: batch insert new articles
        if articles_to_add:
            try:
                for article in articles_to_add:
                    self.db.add(article)

                # Single commit for all articles
                self.db.commit()

                # Refresh to get IDs
                for article in articles_to_add:
                    self.db.refresh(article)
                    article_ids.append(article.id)
                    stored_count += 1

            except IntegrityError as e:
                # Rollback batch and try one-by-one (rare case)
                self.db.rollback()
                print(f"[Ingest] Batch insert failed, falling back to individual inserts: {e}")

                for article in articles_to_add:
                    try:
                        self.db.add(article)
                        self.db.commit()
                        self.db.refresh(article)
                        article_ids.append(article.id)
                        stored_count += 1
                    except IntegrityError:
                        self.db.rollback()
                        print(f"[Ingest] Duplicate detected: {article.external_id}")
                    except Exception as e:
                        self.db.rollback()
                        print(f"[Ingest] Error storing article {article.external_id}: {e}")

            except Exception as e:
                self.db.rollback()
                print(f"[Ingest] Batch insert error: {e}")

        return stored_count, article_ids

    def get_pending_articles(self, limit: int = 50) -> List[Article]:
        """
        Get articles with status 'pending' (not yet ranked).

        Args:
            limit: Max number of articles to return

        Returns:
            List of pending articles
        """
        stmt = (
            select(Article)
            .where(Article.status == "pending")
            .order_by(Article.fetched_at.desc())
            .limit(limit)
        )
        return list(self.db.exec(stmt).all())

    def get_article_by_id(self, article_id: int) -> Article | None:
        """Get article by ID."""
        return self.db.get(Article, article_id)
