from __future__ import annotations

import asyncio
import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

# import feedparser
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from openai import AsyncOpenAI
from sqlmodel import Session, select

from app.database import engine
from app.models import Post


# -----------------------------
# Scheduler setup
# -----------------------------
_scheduler: Optional[AsyncIOScheduler] = None


NEWS_SOURCES: List[Tuple[str, str]] = [
    ("OpenAI Blog", "https://openai.com/blog/rss.xml"),
    ("Google AI", "https://blog.google/technology/ai/rss"),
    ("DeepMind", "https://deepmind.google/blog/rss.xml"),
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("The Verge AI", "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),
    ("MIT Tech Review", "https://www.technologyreview.com/topic/artificial-intelligence/feed"),
]

AUTHORITATIVE_SOURCES = {"OpenAI", "Google AI", "DeepMind"}
KEYWORDS = {"ai", "llm", "genai",
            "artificial intelligence", "machine learning"}


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone="Pacific/Auckland")
        # 07:30 NZDT
        _scheduler.add_job(
            fetch_and_generate_content,
            CronTrigger(hour=7, minute=30, timezone="Pacific/Auckland"),
            name="fetch_generate_0730",
            replace_existing=True,
        )
        # 12:30 NZDT
        _scheduler.add_job(
            fetch_and_generate_content,
            CronTrigger(hour=12, minute=30, timezone="Pacific/Auckland"),
            name="fetch_generate_1230",
            replace_existing=True,
        )
        # 21:00 NZDT
        _scheduler.add_job(
            fetch_and_generate_content,
            CronTrigger(hour=21, minute=0, timezone="Pacific/Auckland"),
            name="fetch_generate_2100",
            replace_existing=True,
        )
        _scheduler.start()
        print("[scheduler] Started AsyncIOScheduler with NZDT cron jobs")
    else:
        if not _scheduler.running:
            _scheduler.start()
            print("[scheduler] Restarted AsyncIOScheduler")


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        print("[scheduler] Stopped AsyncIOScheduler")


def is_running() -> bool:
    return bool(_scheduler and _scheduler.running)


# -----------------------------
# RSS fetching and ranking
# -----------------------------
def fetch_rss_feed(url: str, source_name: str) -> List[Dict[str, Any]]:
    """Temporary stub - RSS disabled due to Python 3.13 compatibility"""
    print(f"[rss] Skipping fetch (RSS temporarily disabled): {source_name}")
    return []


def rank_articles(articles: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], int]]:
    ranked: List[Tuple[Dict[str, Any], int]] = []
    now = datetime.now(timezone.utc)
    for a in articles:
        score = 0
        # Freshness: last 24h
        published: Optional[datetime] = a.get("published")
        if published and (now - published) <= timedelta(hours=24):
            score += 50

        # Authority
        source = str(a.get("source") or "").strip()
        if any(auth in source for auth in AUTHORITATIVE_SOURCES):
            score += 30

        # Keywords in title/summary
        haystack = f"{a.get('title', '')}\n{a.get('summary', '')}".lower()
        for kw in KEYWORDS:
            if kw in haystack:
                score += 5

        ranked.append((a, score))

    ranked.sort(key=lambda t: t[1], reverse=True)
    return ranked


def check_duplicate(url: str, title: str, body: str) -> bool:
    content_hash = hashlib.sha256(
        f"{title}\n{url}\n{body}".encode("utf-8")).hexdigest()
    with Session(engine) as session:
        stmt = select(Post).where(
            (Post.source_url == url) | (Post.content_hash == content_hash)
        )
        exists = session.exec(stmt).first() is not None
    if exists:
        print(f"[dup] Exists by url/hash: {url}")
    return exists


# -----------------------------
# OpenAI generation helpers
# -----------------------------
_openai_client: Optional[AsyncOpenAI] = None


def _get_openai_client() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI()
    return _openai_client


async def generate_text_post(article: Dict[str, Any]) -> List[Dict[str, Any]]:
    client = _get_openai_client()
    prompt = (
        "You are a social copywriter. Create 5 short text posts (120-200 chars).\n"
        "Target platforms: X, LinkedIn, Instagram, Facebook.\n"
        "Use different angles and include 1-2 relevant hashtags each.\n"
        f"Article title: {article.get('title', '')}\n"
        f"Summary: {article.get('summary', '')}\n"
        f"Source: {article.get('source', '')} -> {article.get('url', '')}\n"
        "Return a JSON array of objects with fields: platform (one of X, LinkedIn, Instagram, Facebook), text."
    )
    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Return only valid JSON."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.9,
    )
    content = resp.choices[0].message.content or "[]"
    try:
        data = json.loads(content)
    except Exception:
        print("[openai] JSON parse failed for text posts; returning empty list")
        return []

    results: List[Dict[str, Any]] = []
    for item in data:
        platform = str(item.get("platform", "")).strip() or "General"
        text = str(item.get("text", "")).strip()
        if not text:
            continue
        results.append({"platform": platform, "text": text})
    return results


async def generate_video_script(article: Dict[str, Any]) -> List[str]:
    client = _get_openai_client()
    prompt = (
        "Create 2-3 short video scripts (15-20 seconds).\n"
        "Format each with labeled sections: Hook (0-1.5s), Main (2-8s), Why (9-15s), CTA (16-20s).\n"
        f"Article title: {article.get('title', '')}\n"
        f"Summary: {article.get('summary', '')}\n"
        f"Source: {article.get('source', '')} -> {article.get('url', '')}\n"
        "Return a JSON array of strings, each string is one script."
    )
    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Return only valid JSON."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.9,
    )
    content = resp.choices[0].message.content or "[]"
    try:
        scripts = json.loads(content)
    except Exception:
        print("[openai] JSON parse failed for video scripts; returning empty list")
        return []

    results: List[str] = []
    for s in scripts:
        text = str(s).strip()
        if text:
            results.append(text)
    return results


# -----------------------------
# Main pipeline
# -----------------------------
async def fetch_and_generate_content() -> None:
    print("[job] fetch_and_generate_content started")
    # 1) Fetch
    all_articles: List[Dict[str, Any]] = []
    for source_name, url in NEWS_SOURCES:
        try:
            articles = fetch_rss_feed(url, source_name)
            all_articles.extend(articles)
        except Exception as e:
            print(f"[rss] Error fetching {source_name}: {e}")

    if not all_articles:
        print("[job] No articles fetched")
        return

    # 2) Rank and take top N
    ranked = rank_articles(all_articles)
    top_articles = [a for a, _ in ranked[:12]]  # process up to 12 top articles

    # 3) Process each article
    for article in top_articles:
        title = article.get("title") or ""
        summary = article.get("summary") or ""
        url = article.get("url") or ""
        if not url or not title:
            continue

        if check_duplicate(url, title, summary):
            continue

        # Generate content in parallel
        try:
            text_task = asyncio.create_task(generate_text_post(article))
            video_task = asyncio.create_task(generate_video_script(article))
            text_posts, video_scripts = await asyncio.gather(text_task, video_task)
        except Exception as e:
            print(f"[openai] Error generating content: {e}")
            text_posts, video_scripts = [], []

        content_hash = hashlib.sha256(
            f"{title}\n{url}\n{summary}".encode("utf-8")).hexdigest()

        with Session(engine) as session:
            # Save text posts
            for item in text_posts:
                platforms = [item.get("platform", "General")]
                post = Post(
                    kind="text",
                    title=title,
                    body=item.get("text", "") or "",
                    source_url=url,
                    content_hash=content_hash,
                    tags=[article.get("source", "news")],
                    platforms=platforms,
                    status="draft",
                )
                session.add(post)

            # Save video scripts
            for script in video_scripts:
                post = Post(
                    kind="video",
                    title=title,
                    body=script,
                    source_url=url,
                    content_hash=content_hash,
                    tags=[article.get("source", "news"), "script"],
                    platforms=["Instagram", "TikTok", "YouTube Shorts"],
                    status="draft",
                )
                session.add(post)

            session.commit()
            print(
                f"[db] Saved {len(text_posts)} text + {len(video_scripts)} video for: {title}")

    print("[job] fetch_and_generate_content finished")
