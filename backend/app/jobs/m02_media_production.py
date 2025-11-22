"""
M02 Media Production Job - Voice Generation + B-roll Search

Fetches top-ranked articles from M01, generates voiceovers using ElevenLabs,
searches Pexels for B-roll footage, and saves media files.
"""
# Fix import path: ensure agents module can be found from repo root
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401,E402 guardrails

import argparse  # noqa: E402
import logging  # noqa: E402
import asyncio  # noqa: E402
from typing import Dict, Any, List, Optional  # noqa: E402
from pathlib import Path  # noqa: E402
from datetime import datetime  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Import backend modules
try:
    from app.database import engine
    from app.models import Post, Article, RankingScore, Asset
    from app import tts_service
    from app import video_production
    from sqlmodel import Session, select
    import httpx
except ImportError as e:
    logger.error(f"Failed to import backend modules: {e}")
    logger.error("Make sure PYTHONPATH includes the backend directory")
    sys.exit(1)


# ==================== CONFIGURATION ====================

# Media storage paths (Railway volumes)
MEDIA_BASE_PATH = Path(os.getenv("MEDIA_BASE_PATH", "/app/media"))
VOICE_PATH = MEDIA_BASE_PATH / "voice"
BROLL_PATH = MEDIA_BASE_PATH / "broll"

# Create directories if they don't exist
VOICE_PATH.mkdir(parents=True, exist_ok=True)
BROLL_PATH.mkdir(parents=True, exist_ok=True)

# API Keys
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


# ==================== HELPER FUNCTIONS ====================

async def fetch_top_ranked_articles(
    session: Session,
    min_score: float = 0.6,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Fetch top-ranked articles from M01 that need media production.

    Args:
        session: Database session
        min_score: Minimum ranking score threshold
        limit: Max number of articles to process

    Returns:
        List of article dictionaries with ranking data
    """
    try:
        # Query articles with high ranking scores that haven't been processed
        stmt = (
            select(Article, RankingScore)
            .join(RankingScore, Article.id == RankingScore.article_id)
            .where(
                RankingScore.score >= min_score,
                Article.status == "ranked"  # Only articles that passed ranking
            )
            .order_by(RankingScore.score.desc())
            .limit(limit)
        )

        results = session.exec(stmt).all()

        articles = []
        for article, ranking in results:
            articles.append({
                "id": article.id,
                "title": article.title,
                "description": article.description or "",
                "content": article.content or "",
                "url": article.url,
                "image_url": article.image_url,
                "published_at": article.published_at,
                "ranking_score": ranking.score,
                "category": ranking.category or "general",
            })

        logger.info(f"Found {len(articles)} top-ranked articles for media production")
        return articles

    except Exception as e:
        logger.error(f"Error fetching top-ranked articles: {e}")
        return []


async def generate_voice_for_post(
    post_id: int,
    text: str,
    voice_name: str = "charlotte",
    energy_mode: str = "energetic"
) -> Optional[str]:
    """
    Generate voice audio for a post using ElevenLabs.

    Args:
        post_id: Post ID for file naming
        text: Text to convert to speech
        voice_name: Voice to use (default: charlotte - British female)
        energy_mode: Voice energy preset (energetic, professional, casual)

    Returns:
        Path to saved audio file, or None if failed
    """
    try:
        logger.info(f"Generating voice for post {post_id} with voice '{voice_name}' ({energy_mode})")

        # Generate audio using tts_service
        audio_data = await tts_service.generate_speech(
            text=text,
            voice=voice_name,
            provider="elevenlabs",  # Try ElevenLabs first
            energy_mode=energy_mode
        )

        if not audio_data:
            logger.warning(f"Failed to generate voice for post {post_id}, trying fallback")
            # Try OpenAI TTS as fallback
            audio_data = await tts_service.generate_speech(
                text=text,
                voice="fable",  # British male
                provider="openai",
                energy_mode=energy_mode
            )

        if not audio_data:
            logger.error(f"All TTS providers failed for post {post_id}")
            return None

        # Save audio file
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"post_{post_id}_{timestamp}.mp3"
        file_path = VOICE_PATH / filename

        with open(file_path, "wb") as f:
            f.write(audio_data)

        logger.info(f"Saved voice file: {file_path}")
        return str(file_path)

    except Exception as e:
        logger.error(f"Error generating voice for post {post_id}: {e}")
        import traceback
        traceback.print_exc()
        return None


async def search_broll_footage(
    keywords: List[str],
    duration: int = 10,
    max_results: int = 3
) -> List[Dict[str, str]]:
    """
    Search Pexels for B-roll footage based on keywords.

    Args:
        keywords: List of search keywords
        duration: Minimum duration in seconds
        max_results: Max number of videos to return per keyword

    Returns:
        List of video metadata (url, thumbnail, duration, etc.)
    """
    try:
        if not PEXELS_API_KEY:
            logger.warning("No Pexels API key configured, skipping B-roll search")
            return []

        broll_videos = []

        # Search for each keyword
        for keyword in keywords[:3]:  # Limit to first 3 keywords
            logger.info(f"Searching Pexels for B-roll: '{keyword}'")

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "https://api.pexels.com/videos/search",
                        headers={"Authorization": PEXELS_API_KEY},
                        params={
                            "query": keyword,
                            "per_page": max_results,
                            "orientation": "portrait",  # 9:16 for social media
                        },
                        timeout=30.0
                    )
                    response.raise_for_status()
                    data = response.json()

                # Extract video metadata
                for video in data.get("videos", [])[:max_results]:
                    video_files = video.get("video_files", [])

                    # Find HD portrait video
                    hd_video = None
                    for vf in video_files:
                        if vf.get("quality") == "hd" and vf.get("width", 0) < vf.get("height", 0):
                            hd_video = vf
                            break

                    # Fallback to any HD video
                    if not hd_video:
                        for vf in video_files:
                            if vf.get("quality") == "hd":
                                hd_video = vf
                                break

                    if hd_video:
                        broll_videos.append({
                            "keyword": keyword,
                            "video_url": hd_video.get("link"),
                            "thumbnail": video.get("image"),
                            "duration": video.get("duration", 0),
                            "width": hd_video.get("width", 0),
                            "height": hd_video.get("height", 0),
                            "pexels_id": video.get("id"),
                        })

                logger.info(f"Found {len([v for v in broll_videos if v['keyword'] == keyword])} videos for '{keyword}'")

            except httpx.HTTPError as e:
                logger.warning(f"Pexels API error for keyword '{keyword}': {e}")
                continue

        logger.info(f"Total B-roll videos found: {len(broll_videos)}")
        return broll_videos

    except Exception as e:
        logger.error(f"Error searching B-roll footage: {e}")
        return []


async def create_video_post_from_article(
    session: Session,
    article: Dict[str, Any]
) -> Optional[int]:
    """
    Create a video Post from a ranked Article with generated script.

    Args:
        session: Database session
        article: Article data dictionary

    Returns:
        Post ID if successful, None otherwise
    """
    try:
        # Import script generator
        from app import script_generator

        # Generate viral video script
        scripts = await script_generator.generate_viral_video_scripts(
            article=article,
            num_variants=1,  # Just one for now
            duration=20
        )

        if not scripts:
            logger.error(f"Failed to generate script for article {article['id']}")
            return None

        script_data = scripts[0]
        script_text = script_data.get("script", "")
        hook_type = script_data.get("hook_type", "unknown")

        # Create video Post
        post = Post(
            kind="video",
            title=article["title"],
            body=script_text,
            source_url=article["url"],
            tags=[article["category"], "m02", "auto-generated"],
            platforms=["Instagram", "TikTok", "YouTube Shorts"],
            status="media_production",  # New status for M02 stage
            hook_type=hook_type,
            video_duration=20,
            extra_data={
                "article_id": article["id"],
                "ranking_score": article["ranking_score"],
                "script_generated_at": datetime.utcnow().isoformat(),
            }
        )

        session.add(post)
        session.commit()
        session.refresh(post)

        logger.info(f"Created video post {post.id} from article {article['id']}")
        return post.id

    except Exception as e:
        logger.error(f"Error creating video post from article {article['id']}: {e}")
        import traceback
        traceback.print_exc()
        return None


async def process_media_for_post(
    session: Session,
    post: Post
) -> bool:
    """
    Process media (voice + B-roll) for a single post.

    Args:
        session: Database session
        post: Post object

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Processing media for post {post.id}: {post.title}")

        # 1. Generate voice
        narration_text = f"{post.title}. {post.body}"
        voice_path = await generate_voice_for_post(
            post_id=post.id,
            text=narration_text,
            voice_name="charlotte",  # British female, professional
            energy_mode="energetic"
        )

        if voice_path:
            # Save voice asset
            voice_asset = Asset(
                post_id=post.id,
                type="audio",
                path=voice_path
            )
            session.add(voice_asset)
            logger.info(f"Voice asset created for post {post.id}")
        else:
            logger.warning(f"Failed to generate voice for post {post.id}")

        # 2. Search B-roll footage
        # Extract keywords from title and tags
        keywords = [post.title.split()[0]]  # First word of title
        if post.tags:
            keywords.extend(post.tags[:2])  # First 2 tags

        broll_videos = await search_broll_footage(
            keywords=keywords,
            duration=10,
            max_results=2
        )

        # Save B-roll metadata as assets
        for i, video in enumerate(broll_videos[:3]):  # Max 3 videos
            broll_asset = Asset(
                post_id=post.id,
                type="broll_meta",  # Metadata only, actual download happens in M03
                path=video["video_url"]  # Store URL in path for now
            )
            session.add(broll_asset)
            logger.info(f"B-roll asset {i+1} created for post {post.id}: {video['keyword']}")

        # Update post status
        post.status = "media_ready"  # Ready for M03 video assembly
        post.updated_at = datetime.utcnow()
        session.add(post)
        session.commit()

        logger.info(f"✅ Media processing complete for post {post.id}")
        return True

    except Exception as e:
        logger.error(f"Error processing media for post {post.id}: {e}")
        import traceback
        traceback.print_exc()
        return False


# ==================== MAIN JOB ====================

async def run_m02_media_production(
    min_score: float = 0.6,
    max_articles: int = 5
) -> Dict[str, Any]:
    """
    Main M02 job: Generate media (voice + B-roll) for top-ranked articles.

    Args:
        min_score: Minimum ranking score threshold
        max_articles: Maximum number of articles to process

    Returns:
        Job results summary
    """
    logger.info("=" * 60)
    logger.info("M02 Media Production - Starting")
    logger.info(f"Min score: {min_score}, Max articles: {max_articles}")
    logger.info("=" * 60)

    posts_created = 0
    posts_processed = 0
    errors = []

    try:
        with Session(engine) as session:
            # 1. Fetch top-ranked articles
            articles = await fetch_top_ranked_articles(
                session=session,
                min_score=min_score,
                limit=max_articles
            )

            if not articles:
                logger.warning("No top-ranked articles found for media production")
                return {
                    "status": "completed",
                    "posts_created": 0,
                    "posts_processed": 0,
                    "message": "No articles to process"
                }

            # 2. Create video posts from articles
            post_ids = []
            for article in articles:
                post_id = await create_video_post_from_article(session, article)
                if post_id:
                    post_ids.append(post_id)
                    posts_created += 1

                    # Update article status
                    article_obj = session.get(Article, article["id"])
                    if article_obj:
                        article_obj.status = "scripted"
                        session.add(article_obj)
                        session.commit()

            logger.info(f"Created {posts_created} video posts from articles")

            # 3. Process media for each post
            for post_id in post_ids:
                post = session.get(Post, post_id)
                if post:
                    success = await process_media_for_post(session, post)
                    if success:
                        posts_processed += 1
                    else:
                        errors.append(f"Failed to process media for post {post_id}")

            # Summary
            logger.info("=" * 60)
            logger.info("M02 Media Production - Complete")
            logger.info(f"Posts created: {posts_created}")
            logger.info(f"Posts processed: {posts_processed}")
            logger.info(f"Errors: {len(errors)}")
            logger.info("=" * 60)

            return {
                "status": "completed" if not errors else "partial_failure",
                "posts_created": posts_created,
                "posts_processed": posts_processed,
                "errors": errors if errors else None
            }

    except Exception as e:
        logger.error(f"M02 job failed: {e}", exc_info=True)
        return {
            "status": "failed",
            "posts_created": posts_created,
            "posts_processed": posts_processed,
            "errors": [str(e)]
        }


def main() -> int:
    """
    Main entry point for M02 media production job.

    Returns:
        Exit code: 0 on success, 1 on failure
    """
    parser = argparse.ArgumentParser(description="Run M02 media production")
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.6,
        help="Minimum ranking score threshold (0.0-1.0)"
    )
    parser.add_argument(
        "--max-articles",
        type=int,
        default=5,
        help="Maximum number of articles to process"
    )
    args = parser.parse_args()

    try:
        # Check API keys
        if not ELEVENLABS_API_KEY and not OPENAI_API_KEY:
            logger.warning("No TTS API keys configured (ELEVENLABS_API_KEY or OPENAI_API_KEY)")
            logger.warning("Voice generation may fail")

        if not PEXELS_API_KEY:
            logger.warning("No PEXELS_API_KEY configured")
            logger.warning("B-roll search will be skipped")

        # Run async job
        result = asyncio.run(run_m02_media_production(
            min_score=args.min_score,
            max_articles=args.max_articles
        ))

        if result["status"] == "failed":
            logger.error("M02 job failed")
            return 1
        elif result["status"] == "partial_failure":
            logger.warning("M02 job completed with errors")
            return 0  # Don't fail the workflow for partial failures
        else:
            logger.info("M02 job completed successfully")
            return 0

    except Exception as e:
        logger.error(f"M02 job crashed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
