from __future__ import annotations

from agents.checks.router import should_offload, offload_to_gemini  # guardrails

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from sqlmodel import Session, select

from app.database import engine
from app.models import Asset, Post, PublishLog

# Publer API configuration
PUBLER_API_KEY = os.getenv("PUBLER_API_KEY", "")
PUBLER_API_BASE = "https://publer.io/api/v1"


async def publish_post(post: Post) -> Dict[str, Any]:
    """
    Main function to publish a post to social media platforms.

    Args:
        post: Post object to publish

    Returns:
        Dict with result details: {platform, post_id, url, message}

    Raises:
        Exception: If publishing fails
    """
    try:
        # Get publish result from Publer
        result = await publish_via_publer(post)

        # Log success to PublishLog
        with Session(engine) as session:
            log_entry = PublishLog(
                post_id=post.id if post.id else 0,
                provider="publer",
                platform=",".join(post.platforms or []),
                status="success",
                external_id=result.get("post_id"),
                external_url=result.get("url"),
                created_at=datetime.utcnow(),
            )
            session.add(log_entry)

            # Update post status
            if post.id:
                db_post = session.get(Post, post.id)
                if db_post:
                    db_post.status = "published"
                    db_post.published_at = datetime.utcnow()

            session.commit()

        result["message"] = "Post published successfully"
        return result

    except Exception as e:
        # Log failure to PublishLog
        with Session(engine) as session:
            log_entry = PublishLog(
                post_id=post.id if post.id else 0,
                provider="publer",
                platform=",".join(post.platforms or []),
                status="failed",
                error_message=str(e),
                created_at=datetime.utcnow(),
            )
            session.add(log_entry)

            # Update post status to failed
            if post.id:
                db_post = session.get(Post, post.id)
                if db_post:
                    db_post.status = "failed"

            session.commit()

        raise Exception(f"Publishing failed: {str(e)}")


async def publish_via_publer(post: Post) -> Dict[str, Any]:
    """
    Publish a post using the Publer API.

    Args:
        post: Post object with content to publish

    Returns:
        Dict with platform, post_id, and url

    Raises:
        Exception: If API call fails
    """
    if not PUBLER_API_KEY:
        raise Exception("PUBLER_API_KEY not configured")

    # Build request data
    request_data: Dict[str, Any] = {
        "text": post.body,
        "platforms": post.platforms or [],
    }

    # Handle video posts - upload video asset first
    video_url = None
    if post.kind == "video":
        with Session(engine) as session:
            stmt = select(Asset).where(
                Asset.post_id == post.id, Asset.type == "video"
            )
            video_asset = session.exec(stmt).first()

            if video_asset and video_asset.path:
                # Upload video to Publer (simplified - Publer API documentation may vary)
                video_url = await upload_video_to_publer(video_asset.path)
                request_data["media"] = video_url

    # Add scheduling if scheduled_at is set
    if post.scheduled_at:
        request_data["scheduled_at"] = post.scheduled_at.isoformat()

    # Make API call to Publer
    headers = {
        "Authorization": f"Bearer {PUBLER_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{PUBLER_API_BASE}/scheduled_posts",
                json=request_data,
                headers=headers,
                timeout=30.0,
            )

            if response.status_code not in [200, 201]:
                error_data = response.json() if response.content else {}
                raise Exception(
                    f"Publer API error: {response.status_code} - {error_data.get('message', 'Unknown error')}"
                )

            result_data = response.json()

            return {
                "platform": ",".join(post.platforms or []),
                "post_id": result_data.get("id") or result_data.get("post_id"),
                "url": result_data.get("url") or result_data.get("permalink"),
            }

        except httpx.TimeoutException:
            raise Exception("Publer API request timed out")
        except httpx.RequestError as e:
            raise Exception(f"Publer API connection error: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("Invalid JSON response from Publer API")


async def upload_video_to_publer(file_path: str) -> str:
    """
    Upload a video file to Publer and return the media URL.

    Args:
        file_path: Local path to the video file

    Returns:
        Media URL from Publer

    Raises:
        Exception: If upload fails
    """
    if not os.path.exists(file_path):
        raise Exception(f"Video file not found: {file_path}")

    headers = {
        "Authorization": f"Bearer {PUBLER_API_KEY}",
    }

    async with httpx.AsyncClient() as client:
        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, "video/mp4")}

                response = await client.post(
                    f"{PUBLER_API_BASE}/media",
                    files=files,
                    headers=headers,
                    timeout=120.0,  # Longer timeout for video upload
                )

                if response.status_code not in [200, 201]:
                    error_data = response.json() if response.content else {}
                    raise Exception(
                        f"Video upload error: {response.status_code} - {error_data.get('message', 'Unknown error')}"
                    )

                result_data = response.json()
                return result_data.get("url") or result_data.get("media_url")

        except httpx.TimeoutException:
            raise Exception("Video upload timed out")
        except httpx.RequestError as e:
            raise Exception(f"Video upload connection error: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("Invalid JSON response from video upload")


async def get_publish_status(post_id: int) -> List[Dict[str, Any]]:
    """
    Get publish logs for a specific post.

    Args:
        post_id: Post ID to fetch logs for

    Returns:
        List of publish log entries
    """
    with Session(engine) as session:
        stmt = select(PublishLog).where(PublishLog.post_id == post_id)
        logs = session.exec(stmt).all()

        return [
            {
                "id": log.id,
                "provider": log.provider,
                "platform": log.platform,
                "status": log.status,
                "external_id": log.external_id,
                "external_url": log.external_url,
                "error_message": log.error_message,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]


async def retry_failed_publish(log_id: int) -> Dict[str, Any]:
    """
    Retry a failed publish attempt.

    Args:
        log_id: PublishLog ID to retry

    Returns:
        Result dict from retry attempt

    Raises:
        Exception: If retry fails
    """
    with Session(engine) as session:
        log_entry = session.get(PublishLog, log_id)
        if not log_entry:
            raise Exception("PublishLog entry not found")

        if log_entry.post_id:
            post = session.get(Post, log_entry.post_id)
            if not post:
                raise Exception("Post not found")

            # Increment retry count
            log_entry.retry_count += 1
            session.add(log_entry)
            session.commit()

            # Try publishing again
            return await publish_post(post)
        else:
            raise Exception("No post_id in log entry")
