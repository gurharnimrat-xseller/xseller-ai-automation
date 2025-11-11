from agents.checks.router import should_offload, offload_to_gemini  # guardrails
from __future__ import annotations

import asyncio
import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
# removed per guardrails; use router
# # removed per guardrails; use router
# from openai import AsyncOpenAI
from sqlmodel import Session, select

from app.database import engine
from app.models import Post
from app import video_generator
from app import content_scraper
from app import script_generator


# -----------------------------
# Scheduler setup
# -----------------------------
_scheduler: Optional[AsyncIOScheduler] = None


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
        
        # Process video generation queue every 2 minutes (async job)
        async def process_queue():
            await video_generator.process_video_generation_queue()
        
        _scheduler.add_job(
            process_queue,
            CronTrigger(minute="*/2"),  # Every 2 minutes
            name="process_video_queue",
            replace_existing=True,
        )
        
        _scheduler.start()
        print("[scheduler] Started AsyncIOScheduler with NZDT cron jobs and video processing")
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
# Content fetching (now using content_scraper module)
# -----------------------------


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
    """Generate viral text posts using enhanced script generator."""
    try:
        # Use the new enhanced script generator
        posts = await script_generator.generate_viral_text_posts(
            article=article,
            num_variants=5,
            platforms=["LinkedIn", "Twitter", "Instagram", "Facebook"]
        )

        # Convert to expected format
        results: List[Dict[str, Any]] = []
        for post in posts:
            results.append({
                "platform": post.get("platform", "General"),
                "text": post.get("text", ""),
                "hook_type": post.get("hook_type", "unknown"),
            })

        return results
    except Exception as e:
        print(f"[scheduler] Error generating text posts: {str(e)}")
        return []


async def generate_video_script(article: Dict[str, Any]) -> List[str]:
    """Generate viral video scripts using enhanced script generator."""
    try:
        # Use the new enhanced script generator
        scripts = await script_generator.generate_viral_video_scripts(
            article=article,
            num_variants=3,
            duration=20
        )

        # Convert to expected format (list of script strings)
        results: List[str] = []
        for script_data in scripts:
            script_text = script_data.get("script", "")
            if script_text:
                results.append(script_text)

        return results
    except Exception as e:
        print(f"[scheduler] Error generating video scripts: {str(e)}")
        return []


# -----------------------------
# Main pipeline
# -----------------------------
async def fetch_and_generate_content() -> None:
    print("[job] 🚀 fetch_and_generate_content started")

    # 1) Fetch content from all sources using the new scraper
    try:
        top_articles = await content_scraper.fetch_all_content()
        print(f"[job] ✅ Fetched {len(top_articles)} top-ranked articles")
    except Exception as e:
        print(f"[job] ❌ Error fetching content: {e}")
        import traceback
        traceback.print_exc()
        return

    if not top_articles:
        print("[job] No articles fetched")
        return

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
