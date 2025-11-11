"""
Content Scraper Module
Handles RSS feeds, web scraping, and content aggregation from multiple sources.
"""
from agents.checks.router import should_offload, offload_to_gemini  # guardrails

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import feedparser
import httpx
from bs4 import BeautifulSoup


# ==================== RSS FEED SOURCES ====================

NEWS_SOURCES: List[Tuple[str, str]] = [
    # Primary sources (highly reliable)
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
    ("The Verge AI", "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),

    # Tech news aggregators (very reliable)
    ("Hacker News", "https://hnrss.org/newest?q=AI+OR+GPT+OR+LLM+OR+machine+learning"),
    ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/technology-lab"),
    ("The AI Blog", "https://ai.googleblog.com/feeds/posts/default"),

    # Additional sources (may need fallback)
    ("MIT Tech Review", "https://www.technologyreview.com/topic/artificial-intelligence/feed"),
    ("Wired AI", "https://www.wired.com/feed/tag/ai/latest/rss"),
    ("AI News", "https://artificialintelligence-news.com/feed/"),

    # Corporate blogs (sometimes blocked)
    ("OpenAI Blog", "https://openai.com/blog/rss.xml"),
    ("DeepMind", "https://deepmind.google/blog/rss.xml"),
]

AUTHORITATIVE_SOURCES = {"OpenAI", "Google AI", "DeepMind", "MIT", "Stanford"}
KEYWORDS = {
    "ai", "llm", "gpt", "genai", "chatgpt", "claude",
    "artificial intelligence", "machine learning", "deep learning",
    "neural network", "transformer", "automation", "chatbot"
}


# ==================== RSS FEED FETCHING ====================

def fetch_rss_feed(url: str, source_name: str) -> List[Dict[str, Any]]:
    """
    Fetch and parse RSS feed from a given URL.
    Returns list of articles with title, summary, url, published date, and source.
    """
    try:
        print(f"[scraper] Fetching RSS feed: {source_name} - {url}")

        # Use requests with proper headers to avoid blocking
        import requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        }

        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            feed_content = response.content
        except Exception as e:
            print(f"[scraper] Error fetching {source_name}: {str(e)}")
            # Fallback to feedparser's built-in fetching
            feed_content = url

        # Parse the RSS feed
        feed = feedparser.parse(feed_content)

        if feed.bozo:
            # Feed has parsing issues but might still have entries
            print(f"[scraper] Warning: Feed has parsing issues for {source_name}")

        if not feed.entries:
            print(f"[scraper] No entries found in feed: {source_name}")
            return []

        articles: List[Dict[str, Any]] = []

        for entry in feed.entries[:20]:  # Limit to 20 most recent
            try:
                # Extract article data
                title = entry.get("title", "").strip()
                summary = entry.get("summary", entry.get("description", "")).strip()
                link = entry.get("link", "").strip()

                # Parse published date
                published_parsed = entry.get("published_parsed") or entry.get("updated_parsed")
                if published_parsed:
                    published = datetime(*published_parsed[:6], tzinfo=timezone.utc)
                else:
                    published = datetime.now(timezone.utc)

                # Clean HTML from summary
                summary = clean_html(summary)

                if not title or not link:
                    continue

                article = {
                    "title": title,
                    "summary": summary[:500],  # Limit summary length
                    "url": link,
                    "published": published,
                    "source": source_name,
                    "raw_entry": entry,  # Keep for additional processing if needed
                }

                articles.append(article)

            except Exception as e:
                print(f"[scraper] Error parsing entry from {source_name}: {str(e)}")
                continue

        print(f"[scraper] ✅ Fetched {len(articles)} articles from {source_name}")
        return articles

    except Exception as e:
        print(f"[scraper] ❌ Error fetching RSS feed {source_name}: {str(e)}")
        return []


def clean_html(text: str) -> str:
    """Remove HTML tags and clean up text."""
    if not text:
        return ""

    try:
        # Parse HTML
        soup = BeautifulSoup(text, "html.parser")
        # Extract text
        clean_text = soup.get_text(separator=" ", strip=True)
        # Remove extra whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text
    except Exception:
        # Fallback: simple regex-based cleaning
        clean_text = re.sub(r'<[^>]+>', '', text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text


# ==================== WEB SCRAPING (for non-RSS sources) ====================

async def scrape_webpage(url: str) -> Optional[Dict[str, Any]]:
    """
    Scrape content from a webpage when RSS is not available.
    Extracts title, main content, and metadata.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()

            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            # Extract title
            title = None
            if soup.title:
                title = soup.title.string
            elif soup.find("h1"):
                title = soup.find("h1").get_text(strip=True)

            # Extract main content
            content = extract_main_content(soup)

            # Extract meta description
            meta_desc = ""
            meta_tag = soup.find("meta", attrs={"name": "description"}) or \
                      soup.find("meta", attrs={"property": "og:description"})
            if meta_tag and meta_tag.get("content"):
                meta_desc = meta_tag.get("content")

            # Extract published date
            published = extract_published_date(soup)

            if not title or not content:
                print(f"[scraper] Could not extract title or content from {url}")
                return None

            return {
                "title": title,
                "summary": meta_desc or content[:500],
                "content": content[:2000],  # Limit content length
                "url": url,
                "published": published or datetime.now(timezone.utc),
                "source": urlparse(url).netloc,
            }

    except Exception as e:
        print(f"[scraper] Error scraping webpage {url}: {str(e)}")
        return None


def extract_main_content(soup: BeautifulSoup) -> str:
    """Extract main content from webpage, filtering out nav/footer/ads."""
    # Remove unwanted elements
    for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        element.decompose()

    # Try common article containers
    article_selectors = [
        'article',
        '[role="main"]',
        '.article-content',
        '.post-content',
        '.entry-content',
        'main',
    ]

    for selector in article_selectors:
        content_elem = soup.select_one(selector)
        if content_elem:
            text = content_elem.get_text(separator=" ", strip=True)
            if len(text) > 100:  # Minimum length check
                return text

    # Fallback: extract all paragraph text
    paragraphs = soup.find_all('p')
    text = ' '.join([p.get_text(strip=True) for p in paragraphs])
    return text


def extract_published_date(soup: BeautifulSoup) -> Optional[datetime]:
    """Try to extract published date from webpage metadata."""
    # Try meta tags
    date_selectors = [
        ("meta", {"property": "article:published_time"}),
        ("meta", {"name": "publishdate"}),
        ("meta", {"name": "date"}),
        ("time", {"datetime": True}),
    ]

    for tag_name, attrs in date_selectors:
        tag = soup.find(tag_name, attrs=attrs)
        if tag:
            date_str = tag.get("content") or tag.get("datetime")
            if date_str:
                try:
                    # Try parsing ISO format
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except Exception:
                    pass

    return None


# ==================== ARTICLE RANKING & FILTERING ====================

def rank_articles(articles: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], int]]:
    """
    Rank articles by relevance score based on:
    - Freshness (published date)
    - Authority (source reputation)
    - Keywords (AI/tech relevance)
    - Engagement potential
    """
    from datetime import timedelta

    ranked: List[Tuple[Dict[str, Any], int]] = []
    now = datetime.now(timezone.utc)

    for article in articles:
        score = 0

        # 1. Freshness Score (0-50 points)
        published: Optional[datetime] = article.get("published")
        if published:
            age = now - published
            if age <= timedelta(hours=6):
                score += 50  # Very fresh
            elif age <= timedelta(hours=24):
                score += 40  # Fresh
            elif age <= timedelta(days=3):
                score += 25  # Recent
            elif age <= timedelta(days=7):
                score += 10  # This week

        # 2. Authority Score (0-30 points)
        source = str(article.get("source", "")).strip()
        if any(auth.lower() in source.lower() for auth in AUTHORITATIVE_SOURCES):
            score += 30

        # 3. Keyword Relevance (0-30 points)
        haystack = f"{article.get('title', '')}\n{article.get('summary', '')}".lower()
        keyword_matches = sum(1 for kw in KEYWORDS if kw in haystack)
        score += min(keyword_matches * 5, 30)  # Cap at 30 points

        # 4. Title Quality (0-20 points)
        title = article.get("title", "")
        if title:
            # Longer, descriptive titles score higher
            if len(title) > 40:
                score += 10
            # Titles with numbers/data tend to perform well
            if re.search(r'\d+', title):
                score += 5
            # Question titles engage readers
            if '?' in title:
                score += 5

        ranked.append((article, score))

    # Sort by score (highest first)
    ranked.sort(key=lambda t: t[1], reverse=True)

    return ranked


def filter_duplicates(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter out duplicate articles based on URL and content similarity.
    """
    seen_urls = set()
    seen_hashes = set()
    unique_articles = []

    for article in articles:
        url = article.get("url", "")
        title = article.get("title", "")
        summary = article.get("summary", "")

        # Check URL duplicate
        if url in seen_urls:
            continue

        # Check content similarity via hash
        content_hash = hashlib.sha256(
            f"{title}\n{summary}".encode("utf-8")
        ).hexdigest()

        if content_hash in seen_hashes:
            continue

        seen_urls.add(url)
        seen_hashes.add(content_hash)
        unique_articles.append(article)

    return unique_articles


# ==================== MAIN SCRAPING FUNCTION ====================

async def fetch_all_content() -> List[Dict[str, Any]]:
    """
    Fetch content from all sources (RSS feeds + web scraping).
    Returns ranked and filtered list of articles.
    """
    print("[scraper] 🚀 Starting content fetch from all sources...")

    all_articles: List[Dict[str, Any]] = []

    # 1. Fetch RSS feeds
    for source_name, url in NEWS_SOURCES:
        try:
            articles = fetch_rss_feed(url, source_name)
            all_articles.extend(articles)
        except Exception as e:
            print(f"[scraper] Error with {source_name}: {str(e)}")

    print(f"[scraper] Total articles fetched: {len(all_articles)}")

    # 2. Filter duplicates
    unique_articles = filter_duplicates(all_articles)
    print(f"[scraper] Unique articles after dedup: {len(unique_articles)}")

    # 3. Rank articles
    ranked = rank_articles(unique_articles)

    # 4. Return top N articles
    top_articles = [article for article, score in ranked[:15]]

    print(f"[scraper] ✅ Returning top {len(top_articles)} articles")

    # Print top 5 for debugging
    for i, (article, score) in enumerate(ranked[:5], 1):
        print(f"  {i}. [{score}pts] {article['title'][:60]}... - {article['source']}")

    return top_articles


# ==================== UTILITY FUNCTIONS ====================

def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """Extract key topics/keywords from text for better content categorization."""
    # Simple keyword extraction (in production, use NLP libraries)
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())

    # Filter out common words
    common_words = {'that', 'this', 'with', 'from', 'have', 'been', 'will', 'there', 'what', 'about'}
    keywords = [w for w in words if w not in common_words and w in KEYWORDS]

    # Return unique keywords
    return list(dict.fromkeys(keywords))[:max_keywords]
