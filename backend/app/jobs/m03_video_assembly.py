"""
M03 Video Assembly Job - Combine Voice + B-roll + Overlays

Takes posts with media_ready status from M02, downloads B-roll footage,
combines with voice audio, adds text overlays, and generates final videos.
"""
# Fix import path: ensure agents module can be found from repo root
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401,E402 guardrails

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
    from app.models import Post, Asset
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
VIDEO_PATH = MEDIA_BASE_PATH / "videos"
BROLL_PATH = MEDIA_BASE_PATH / "broll"
TEMP_PATH = MEDIA_BASE_PATH / "temp"

# Create directories if they don't exist
VIDEO_PATH.mkdir(parents=True, exist_ok=True)
BROLL_PATH.mkdir(parents=True, exist_ok=True)
TEMP_PATH.mkdir(parents=True, exist_ok=True)

# Video settings
VIDEO_QUALITY = os.getenv("VIDEO_QUALITY", "medium")  # low, medium, high
VIDEO_FPS = int(os.getenv("VIDEO_FPS", "30"))


# ==================== HELPER FUNCTIONS ====================

async def fetch_media_ready_posts(
    session: Session,
    limit: int = 10
) -> List[Post]:
    """
    Fetch posts with media_ready status (ready for video assembly).

    Args:
        session: Database session
        limit: Max number of posts to process

    Returns:
        List of Post objects
    """
    try:
        stmt = (
            select(Post)
            .where(Post.status == "media_ready")
            .order_by(Post.created_at.desc())
            .limit(limit)
        )

        posts = session.exec(stmt).all()
        logger.info(f"Found {len(posts)} posts ready for video assembly")
        return list(posts)

    except Exception as e:
        logger.error(f"Error fetching media-ready posts: {e}")
        return []


async def download_broll_video(
    video_url: str,
    post_id: int,
    index: int = 0
) -> Optional[str]:
    """
    Download B-roll video from Pexels URL.

    Args:
        video_url: Pexels video URL
        post_id: Post ID for file naming
        index: Video index (for multiple B-rolls)

    Returns:
        Path to downloaded video file, or None if failed
    """
    try:
        logger.info(f"Downloading B-roll video {index} for post {post_id}")

        # Download video
        async with httpx.AsyncClient() as client:
            response = await client.get(video_url, timeout=120.0, follow_redirects=True)
            response.raise_for_status()

        # Save to file
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"broll_post{post_id}_idx{index}_{timestamp}.mp4"
        file_path = BROLL_PATH / filename

        with open(file_path, "wb") as f:
            f.write(response.content)

        logger.info(f"Downloaded B-roll video: {file_path} ({len(response.content) / 1024:.1f} KB)")
        return str(file_path)

    except httpx.HTTPError as e:
        logger.error(f"HTTP error downloading B-roll video: {e}")
        return None
    except Exception as e:
        logger.error(f"Error downloading B-roll video: {e}")
        import traceback
        traceback.print_exc()
        return None


async def assemble_video_for_post(
    session: Session,
    post: Post
) -> Optional[str]:
    """
    Assemble final video for a post using voice + B-roll + overlays.

    Args:
        session: Database session
        post: Post object with media assets

    Returns:
        Path to assembled video file, or None if failed
    """
    try:
        logger.info(f"Assembling video for post {post.id}: {post.title}")

        # 1. Get voice asset
        voice_asset_stmt = select(Asset).where(
            Asset.post_id == post.id,
            Asset.type == "audio"
        ).limit(1)
        voice_asset = session.exec(voice_asset_stmt).first()

        if not voice_asset:
            logger.warning(f"No voice asset found for post {post.id}")
            voice_path = None
        else:
            voice_path = voice_asset.path
            if not os.path.exists(voice_path):
                logger.warning(f"Voice file not found: {voice_path}")
                voice_path = None
            else:
                logger.info(f"Voice file: {voice_path}")

        # 2. Get B-roll assets
        broll_assets_stmt = select(Asset).where(
            Asset.post_id == post.id,
            Asset.type == "broll_meta"
        )
        broll_assets = session.exec(broll_assets_stmt).all()

        # Download B-roll videos
        broll_paths = []
        for i, broll_asset in enumerate(broll_assets[:3]):  # Max 3 B-rolls
            broll_url = broll_asset.path  # URL stored in path field
            broll_path = await download_broll_video(broll_url, post.id, i)
            if broll_path:
                broll_paths.append(broll_path)

        logger.info(f"Downloaded {len(broll_paths)} B-roll videos for post {post.id}")

        # 3. Determine video generation strategy
        # Check if MoviePy is available
        try:
            from moviepy.editor import VideoFileClip  # noqa: F401
            moviepy_available = True
        except ImportError:
            moviepy_available = False
            logger.warning("MoviePy not available - will use simplified video generation")

        # 4. Generate video
        if moviepy_available and broll_paths:
            # Full video assembly with MoviePy
            result = await _assemble_with_moviepy(
                post=post,
                voice_path=voice_path,
                broll_paths=broll_paths
            )
        else:
            # Simplified approach: Use existing video_production module
            result = await video_production.generate_video_from_script(
                script=post.body,
                title=post.title,
                add_voiceover=(voice_path is not None)
            )

        if not result.get("success"):
            logger.error(f"Video generation failed for post {post.id}: {result.get('error')}")
            return None

        video_path = result.get("video_path")
        logger.info(f"✅ Video assembled successfully: {video_path}")
        return video_path

    except Exception as e:
        logger.error(f"Error assembling video for post {post.id}: {e}")
        import traceback
        traceback.print_exc()
        return None


async def _assemble_with_moviepy(
    post: Post,
    voice_path: Optional[str],
    broll_paths: List[str]
) -> Dict[str, Any]:
    """
    Assemble video using MoviePy with B-roll footage.

    Args:
        post: Post object
        voice_path: Path to voice audio file
        broll_paths: List of B-roll video file paths

    Returns:
        Dict with success status and video path
    """
    try:
        from moviepy.editor import (
            VideoFileClip, AudioFileClip, CompositeVideoClip,
            concatenate_videoclips, ColorClip, TextClip
        )
        from moviepy.video.fx.all import resize, fadein, fadeout

        logger.info("Assembling video with MoviePy")

        # Target duration (based on script or default 20s)
        target_duration = post.video_duration or 20

        # 1. Load and prepare B-roll clips
        broll_clips = []
        for broll_path in broll_paths:
            try:
                clip = VideoFileClip(broll_path)

                # Resize to 9:16 aspect ratio (1080x1920)
                clip = resize(clip, height=1920)

                # Crop to center if needed
                if clip.w > 1080:
                    x_center = clip.w // 2
                    clip = clip.crop(x1=x_center - 540, x2=x_center + 540)

                broll_clips.append(clip)
            except Exception as e:
                logger.warning(f"Failed to load B-roll {broll_path}: {e}")
                continue

        if not broll_clips:
            logger.warning("No valid B-roll clips, using color background")
            # Create black background
            bg_clip = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=target_duration)
            broll_clips = [bg_clip]

        # 2. Create base video from B-roll
        # Distribute duration across clips
        clips_per_duration = target_duration / len(broll_clips)

        final_clips = []
        for clip in broll_clips:
            # Trim to allocated duration
            if clip.duration > clips_per_duration:
                clip = clip.subclip(0, clips_per_duration)

            # Add fade transitions
            clip = fadein(clip, 0.5)
            clip = fadeout(clip, 0.5)

            final_clips.append(clip)

        # Concatenate B-roll clips
        base_video = concatenate_videoclips(final_clips, method="compose")

        # 3. Add voice audio if available
        if voice_path and os.path.exists(voice_path):
            try:
                audio_clip = AudioFileClip(voice_path)
                # Match audio duration to video
                if audio_clip.duration < base_video.duration:
                    # Video longer than audio - trim video
                    base_video = base_video.subclip(0, audio_clip.duration)
                elif audio_clip.duration > base_video.duration:
                    # Audio longer than video - trim audio
                    audio_clip = audio_clip.subclip(0, base_video.duration)

                base_video = base_video.set_audio(audio_clip)
                logger.info("Voice audio added to video")
            except Exception as e:
                logger.warning(f"Failed to add voice audio: {e}")

        # 4. Add text overlays (title at top)
        try:
            # Create title overlay
            title_text = post.title[:50]  # Limit length

            # Use TextClip if available, otherwise skip
            try:
                title_clip = TextClip(
                    title_text,
                    fontsize=60,
                    color='white',
                    bg_color='black',
                    size=(1000, None),
                    method='caption'
                ).set_position(('center', 100)).set_duration(min(5, base_video.duration))

                # Composite video with title
                final_video = CompositeVideoClip([base_video, title_clip])
            except Exception as e:
                logger.warning(f"TextClip not available or failed: {e}")
                final_video = base_video
        except Exception as e:
            logger.warning(f"Failed to add text overlay: {e}")
            final_video = base_video

        # 5. Export video
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"video_post{post.id}_{timestamp}.mp4"
        output_path = VIDEO_PATH / filename

        logger.info(f"Exporting video to: {output_path}")

        final_video.write_videofile(
            str(output_path),
            fps=VIDEO_FPS,
            codec='libx264',
            preset='medium',
            threads=4,
            audio=True,
            logger='bar'
        )

        # Clean up
        final_video.close()
        for clip in broll_clips:
            clip.close()

        logger.info(f"✅ Video exported successfully: {output_path}")

        return {
            "success": True,
            "video_path": str(output_path),
            "duration": base_video.duration
        }

    except Exception as e:
        logger.error(f"MoviePy assembly failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


# ==================== MAIN JOB ====================

async def run_m03_video_assembly(
    max_posts: int = 5
) -> Dict[str, Any]:
    """
    Main M03 job: Assemble videos from media-ready posts.

    Args:
        max_posts: Maximum number of posts to process

    Returns:
        Job results summary
    """
    logger.info("=" * 60)
    logger.info("M03 Video Assembly - Starting")
    logger.info(f"Max posts: {max_posts}")
    logger.info("=" * 60)

    posts_processed = 0
    videos_created = 0
    errors = []

    try:
        with Session(engine) as session:
            # 1. Fetch media-ready posts
            posts = await fetch_media_ready_posts(
                session=session,
                limit=max_posts
            )

            if not posts:
                logger.warning("No posts ready for video assembly")
                return {
                    "status": "completed",
                    "posts_processed": 0,
                    "videos_created": 0,
                    "message": "No posts to process"
                }

            # 2. Assemble video for each post
            for post in posts:
                logger.info(f"Processing post {post.id}: {post.title}")
                posts_processed += 1

                # Assemble video
                video_path = await assemble_video_for_post(session, post)

                if video_path:
                    # Create video asset
                    video_asset = Asset(
                        post_id=post.id,
                        type="video",
                        path=video_path
                    )
                    session.add(video_asset)

                    # Update post status
                    post.status = "ready_for_review"  # Ready for M04 review
                    post.updated_at = datetime.utcnow()
                    session.add(post)
                    session.commit()

                    videos_created += 1
                    logger.info(f"✅ Video created for post {post.id}")
                else:
                    # Mark post as failed
                    post.status = "video_failed"
                    post.updated_at = datetime.utcnow()
                    session.add(post)
                    session.commit()

                    errors.append(f"Failed to create video for post {post.id}")
                    logger.error(f"❌ Video creation failed for post {post.id}")

            # Summary
            logger.info("=" * 60)
            logger.info("M03 Video Assembly - Complete")
            logger.info(f"Posts processed: {posts_processed}")
            logger.info(f"Videos created: {videos_created}")
            logger.info(f"Errors: {len(errors)}")
            logger.info("=" * 60)

            return {
                "status": "completed" if not errors else "partial_failure",
                "posts_processed": posts_processed,
                "videos_created": videos_created,
                "errors": errors if errors else None
            }

    except Exception as e:
        logger.error(f"M03 job failed: {e}", exc_info=True)
        return {
            "status": "failed",
            "posts_processed": posts_processed,
            "videos_created": videos_created,
            "errors": [str(e)]
        }


def main() -> int:
    """
    Main entry point for M03 video assembly job.

    Returns:
        Exit code: 0 on success, 1 on failure
    """
    parser = argparse.ArgumentParser(description="Run M03 video assembly")
    parser.add_argument(
        "--max-posts",
        type=int,
        default=5,
        help="Maximum number of posts to process"
    )
    args = parser.parse_args()

    try:
        # Check MoviePy availability
        try:
            from moviepy.editor import VideoFileClip  # noqa: F401
            logger.info("MoviePy available - full video assembly enabled")
        except ImportError:
            logger.warning("MoviePy not available - using simplified video generation")
            logger.warning("Install MoviePy for full features: pip install moviepy")

        # Run async job
        result = asyncio.run(run_m03_video_assembly(
            max_posts=args.max_posts
        ))

        if result["status"] == "failed":
            logger.error("M03 job failed")
            return 1
        elif result["status"] == "partial_failure":
            logger.warning("M03 job completed with errors")
            return 0  # Don't fail the workflow for partial failures
        else:
            logger.info("M03 job completed successfully")
            return 0

    except Exception as e:
        logger.error(f"M03 job crashed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
