"""
Test M01 news ingestion and ranking API endpoints.

This test can be run locally or in CI to verify the 502 fix is working.
"""
import pytest
import requests
import os


def test_news_ingest_no_502():
    """
    Verify POST /api/news/ingest returns 200 (not 502) and includes article_ids.

    This test specifically validates the 502 fix:
    - Ensures the endpoint responds within timeout
    - Verifies article_ids field is present in response
    - Confirms no "Application failed to respond" error
    """
    # Get backend URL from environment or use localhost
    base_url = os.getenv("BACKEND_API_BASE_URL", "http://localhost:8000")

    # Call ingestion endpoint
    response = requests.post(
        f"{base_url}/api/news/ingest",
        json={
            "sources": ["mock"],  # Use mock to avoid external API dependency
            "limit_per_source": 5
        },
        timeout=30  # Should complete well within 30 seconds
    )

    # Assert no 502 error
    assert response.status_code != 502, f"Got 502 error: {response.text}"

    # Assert successful response
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Parse response
    data = response.json()

    # Verify required fields (including article_ids)
    assert "job_id" in data, "Missing job_id in response"
    assert "status" in data, "Missing status in response"
    assert "articles_fetched" in data, "Missing articles_fetched in response"
    assert "article_ids" in data, "Missing article_ids in response (this was the bug!)"

    # Verify article_ids is a list
    assert isinstance(data["article_ids"], list), "article_ids should be a list"

    print(f"✅ Test passed! Ingestion returned {len(data['article_ids'])} article IDs")
    print(f"   Response: job_id={data['job_id']}, status={data['status']}, articles={data['articles_fetched']}")


def test_news_rank_with_article_ids():
    """
    Verify POST /api/news/rank works with article_ids from ingestion.

    This is an end-to-end test of the complete M01 pipeline.
    """
    base_url = os.getenv("BACKEND_API_BASE_URL", "http://localhost:8000")

    # Step 1: Ingest articles
    ingest_response = requests.post(
        f"{base_url}/api/news/ingest",
        json={
            "sources": ["mock"],
            "limit_per_source": 3
        },
        timeout=30
    )

    assert ingest_response.status_code == 200, f"Ingestion failed: {ingest_response.text}"

    ingest_data = ingest_response.json()
    article_ids = ingest_data.get("article_ids", [])

    # Skip ranking if no articles (might be duplicates)
    if not article_ids:
        pytest.skip("No articles to rank (likely all duplicates)")

    # Step 2: Rank articles
    rank_response = requests.post(
        f"{base_url}/api/news/rank",
        json={
            "article_ids": article_ids,
            "force_rerank": False
        },
        timeout=60
    )

    assert rank_response.status_code == 200, f"Ranking failed: {rank_response.text}"

    rank_data = rank_response.json()

    # Verify ranking response structure
    assert "ranked_count" in rank_data, "Missing ranked_count in ranking response"
    assert "skipped_count" in rank_data, "Missing skipped_count in ranking response"
    assert "scores" in rank_data, "Missing scores in ranking response"

    print("✅ End-to-end test passed!")
    print(f"   Ingested {len(article_ids)} articles")
    print(f"   Ranked {rank_data['ranked_count']}, skipped {rank_data['skipped_count']}")


if __name__ == "__main__":
    """Allow running as a standalone script for quick verification."""
    print("=" * 60)
    print("M01 API Verification Test")
    print("=" * 60)

    try:
        print("\n1. Testing /api/news/ingest (502 fix)...")
        test_news_ingest_no_502()

        print("\n2. Testing end-to-end pipeline...")
        test_news_rank_with_article_ids()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - M01 502 issue is fixed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
