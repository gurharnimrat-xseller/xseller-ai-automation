"""
M01 Daily Batch Job - News Ingestion + Ranking Pipeline

Orchestrates the daily execution of M01A news ingestion and ranking.
Calls the backend API endpoints to trigger the pipeline.
"""
from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401 guardrails

import argparse
import logging
import sys
from typing import Dict, Any, List
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run M01 daily batch: news ingestion + ranking"
    )
    parser.add_argument(
        "--base-url",
        required=True,
        help="Backend API base URL (e.g., https://api.xseller.ai)"
    )
    parser.add_argument(
        "--sources",
        required=True,
        help="Comma-separated list of news sources (e.g., 'newsapi,mock')"
    )
    parser.add_argument(
        "--limit-per-source",
        type=int,
        required=True,
        help="Maximum articles to fetch per source"
    )
    parser.add_argument(
        "--min-score",
        type=float,
        required=True,
        help="Minimum ranking score threshold (0.0-1.0)"
    )
    return parser.parse_args()


def run_ingestion(
    base_url: str,
    sources: List[str],
    limit_per_source: int
) -> Dict[str, Any]:
    """
    Trigger news ingestion via API.

    Args:
        base_url: Backend API base URL
        sources: List of news source identifiers
        limit_per_source: Max articles per source

    Returns:
        Response JSON with ingestion results

    Raises:
        requests.HTTPError: If API call fails
    """
    url = f"{base_url.rstrip('/')}/api/news/ingest"
    payload = {
        "sources": sources,
        "limit_per_source": limit_per_source
    }

    logger.info(f"Triggering ingestion: {payload}")
    response = requests.post(url, json=payload, timeout=300)
    response.raise_for_status()

    result = response.json()
    logger.info(f"Ingestion complete: {result.get('articles_fetched', 0)} articles fetched")
    return result


def run_ranking(
    base_url: str,
    article_ids: List[int],
    min_score: float
) -> Dict[str, Any]:
    """
    Trigger news ranking via API.

    Args:
        base_url: Backend API base URL
        article_ids: List of article IDs to rank
        min_score: Minimum score threshold

    Returns:
        Response JSON with ranking results

    Raises:
        requests.HTTPError: If API call fails
    """
    url = f"{base_url.rstrip('/')}/api/news/rank"
    payload = {
        "article_ids": article_ids,
        "min_score": min_score,
        "force_rerank": False
    }

    logger.info(f"Triggering ranking for {len(article_ids)} articles (min_score={min_score})")
    response = requests.post(url, json=payload, timeout=600)
    response.raise_for_status()

    result = response.json()
    ranked_count = len(result.get("ranked_articles", []))
    logger.info(f"Ranking complete: {ranked_count} articles ranked")
    return result


def main() -> int:
    """
    Main entry point for M01 daily batch job.

    Returns:
        Exit code: 0 on success, 1 on failure
    """
    args = parse_args()

    try:
        # Parse sources
        sources = [s.strip() for s in args.sources.split(",") if s.strip()]
        if not sources:
            logger.error("No valid sources provided")
            return 1

        # Step 1: Run ingestion
        logger.info("=" * 60)
        logger.info("M01 Daily Batch - Starting")
        logger.info(f"Base URL: {args.base_url}")
        logger.info(f"Sources: {sources}")
        logger.info(f"Limit per source: {args.limit_per_source}")
        logger.info(f"Min score: {args.min_score}")
        logger.info("=" * 60)

        ingest_result = run_ingestion(
            base_url=args.base_url,
            sources=sources,
            limit_per_source=args.limit_per_source
        )

        # Extract article IDs from ingestion result
        article_ids = ingest_result.get("article_ids", [])
        if not article_ids:
            logger.warning("No articles to rank (ingestion returned 0 articles)")
            logger.info("M01 Daily Batch - Complete (no ranking needed)")
            return 0

        # Step 2: Run ranking
        rank_result = run_ranking(
            base_url=args.base_url,
            article_ids=article_ids,
            min_score=args.min_score
        )

        # Summary
        logger.info("=" * 60)
        logger.info("M01 Daily Batch - Complete")
        logger.info(f"Articles fetched: {ingest_result.get('articles_fetched', 0)}")
        logger.info(f"Articles ranked: {len(rank_result.get('ranked_articles', []))}")
        logger.info("=" * 60)

        return 0

    except requests.HTTPError as e:
        logger.error(f"API request failed: {e}")
        if e.response is not None:
            logger.error(f"Response body: {e.response.text}")
        return 1
    except Exception as e:
        logger.error(f"Batch job failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
