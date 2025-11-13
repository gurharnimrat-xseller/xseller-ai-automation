"""
News source clients for fetching articles from external providers.

Provides a unified interface for different news sources with retry logic and error handling.
"""

from agents.checks.router import should_offload, offload_to_gemini  # guardrails

import time
import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import requests


# ==================== Configuration ====================


class NewsSourceConfig(BaseModel):
    """Configuration for a news source."""
    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = Field(default=10, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Max retry attempts")


class NewsArticleRaw(BaseModel):
    """Normalized structure for raw article data from any source."""
    source_name: str
    external_id: str
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    published_at: datetime


# ==================== Retry Decorator ====================


def retry_with_backoff(max_retries: int = 3, base_delay: float = 0.5):
    """
    Decorator for retry with exponential backoff + jitter.

    Follows the pattern from docs/style/python_retry_backoff.md
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        raise
                    sleep_time = delay * (4 ** (attempt - 1))
                    sleep_time += random.uniform(0, 0.3)  # Add jitter
                    print(f"[retry] Attempt {attempt} failed: {e}. Retrying in {sleep_time:.2f}s")
                    time.sleep(sleep_time)
            return None
        return wrapper
    return decorator


# ==================== News API Client ====================


class NewsAPIClient:
    """Client for NewsAPI.org."""

    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "XSeller-NewsBot/1.0"
        })

    @retry_with_backoff(max_retries=3)
    def fetch_top_headlines(self, limit: int = 10, category: Optional[str] = None) -> List[NewsArticleRaw]:
        """
        Fetch top headlines from NewsAPI.

        Args:
            limit: Max number of articles to fetch
            category: Optional category filter (business, tech, etc.)

        Returns:
            List of normalized articles
        """
        params = {
            "apiKey": self.api_key,
            "pageSize": min(limit, 100),
            "language": "en",
            "country": "us"
        }

        if category:
            params["category"] = category

        response = self.session.get(
            f"{self.base_url}/top-headlines",
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()

        data = response.json()

        if data.get("status") != "ok":
            raise Exception(f"NewsAPI error: {data.get('message', 'Unknown error')}")

        articles = []
        for item in data.get("articles", [])[:limit]:
            # Skip articles without required fields
            if not item.get("title") or not item.get("url"):
                continue

            # Generate external_id from URL hash
            external_id = f"newsapi_{hash(item['url'])}"

            # Parse published date
            published_str = item.get("publishedAt", "")
            try:
                published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
            except Exception:
                published_at = datetime.utcnow()

            article = NewsArticleRaw(
                source_name="newsapi",
                external_id=external_id,
                title=item.get("title", ""),
                description=item.get("description"),
                content=item.get("content"),
                url=item["url"],
                image_url=item.get("urlToImage"),
                published_at=published_at
            )
            articles.append(article)

        return articles


# ==================== Mock News Client ====================


class MockNewsClient:
    """Mock news client for testing without external API calls."""

    def __init__(self):
        self.mock_articles = [
            {
                "title": "AI Breakthrough: New Model Achieves Human-Level Understanding",
                "description": "Researchers announce a groundbreaking AI model that demonstrates unprecedented understanding of complex tasks.",
                "url": "https://example.com/ai-breakthrough",
                "category": "tech"
            },
            {
                "title": "Global Markets Rally on Strong Economic Data",
                "description": "Stock markets worldwide see significant gains following positive economic indicators.",
                "url": "https://example.com/markets-rally",
                "category": "business"
            },
            {
                "title": "New Study Reveals Benefits of Remote Work",
                "description": "Comprehensive research shows improved productivity and employee satisfaction with remote work arrangements.",
                "url": "https://example.com/remote-work-study",
                "category": "business"
            },
            {
                "title": "Tech Giant Announces Revolutionary Product Launch",
                "description": "Major technology company unveils innovative product expected to transform the industry.",
                "url": "https://example.com/product-launch",
                "category": "tech"
            },
            {
                "title": "Climate Initiative Shows Promising Results",
                "description": "New environmental program demonstrates significant impact in reducing carbon emissions.",
                "url": "https://example.com/climate-initiative",
                "category": "environment"
            }
        ]

    def fetch_top_headlines(self, limit: int = 10, category: Optional[str] = None) -> List[NewsArticleRaw]:
        """
        Return mock articles for testing.

        Args:
            limit: Max number of articles to return
            category: Optional category filter

        Returns:
            List of mock articles
        """
        filtered = self.mock_articles
        if category:
            filtered = [a for a in filtered if a.get("category") == category]

        articles = []
        for idx, item in enumerate(filtered[:limit]):
            article = NewsArticleRaw(
                source_name="mock",
                external_id=f"mock_{idx}_{hash(item['url'])}",
                title=item["title"],
                description=item.get("description"),
                content=item.get("description"),  # Use description as content for mock
                url=item["url"],
                image_url=f"https://via.placeholder.com/400x300?text=Article+{idx+1}",
                published_at=datetime.utcnow() - timedelta(hours=idx)
            )
            articles.append(article)

        return articles


# ==================== Factory Function ====================


def get_news_client(source_name: str, api_key: Optional[str] = None, config: Optional[NewsSourceConfig] = None):
    """
    Factory function to get the appropriate news client.

    Args:
        source_name: Name of the source ('newsapi', 'mock')
        api_key: API key for the source (if required)
        config: Optional configuration override

    Returns:
        News client instance

    Raises:
        ValueError: If source_name is not supported or API key is missing
    """
    source_name = source_name.lower()

    if source_name == "newsapi":
        if not api_key:
            raise ValueError("API key required for NewsAPI")
        timeout = config.timeout if config else 10
        return NewsAPIClient(api_key=api_key, timeout=timeout)

    elif source_name == "mock":
        return MockNewsClient()

    else:
        raise ValueError(f"Unsupported news source: {source_name}")
