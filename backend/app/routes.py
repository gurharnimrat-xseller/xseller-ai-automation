from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlmodel import Session, select, func

from app.database import engine
from app.models import Post, PublishLog
from app import publishing

# Create router
router = APIRouter()


# Dependency to get database session
def get_session() -> Session:
    with Session(engine) as session:
        yield session


# ==================== Dashboard Stats ====================

@router.get("/api/stats/dashboard")
async def get_dashboard_stats(session: Session = Depends(get_session)) -> Dict[str, Any]:
    """Get dashboard statistics and recent activity."""
    try:
        # Count posts by status
        draft_count = session.exec(
            select(func.count()).select_from(Post).where(
                Post.status == "draft",
                Post.deleted_at.is_(None)
            )
        ).one()

        approved_count = session.exec(
            select(func.count()).select_from(Post).where(
                Post.status == "approved",
                Post.deleted_at.is_(None)
            )
        ).one()

        # Published today
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        published_today_count = session.exec(
            select(func.count()).select_from(Post).where(
                Post.status == "published",
                Post.published_at >= today,
                Post.deleted_at.is_(None)
            )
        ).one()

        # Overdue (approved but scheduled_at < now)
        now = datetime.utcnow()
        overdue_count = session.exec(
            select(func.count()).select_from(Post).where(
                Post.status == "approved",
                Post.scheduled_at.isnot(None),
                Post.scheduled_at < now,
                Post.deleted_at.is_(None)
            )
        ).one()

        # Failed
        failed_count = session.exec(
            select(func.count()).select_from(Post).where(
                Post.status == "failed",
                Post.deleted_at.is_(None)
            )
        ).one()

        return {
            "queue_stats": {
                "draft": draft_count,
                "approved": approved_count,
                "published_today": published_today_count,
                "overdue": overdue_count,
                "failed": failed_count,
            },
            "recent_activity": [],  # TODO: Implement recent activity
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching stats: {str(e)}")


# ==================== Content Queue ====================

@router.get("/api/content/queue")
async def get_queue(
    status: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Get content queue with optional filters."""
    try:
        # Build query
        stmt = select(Post).where(Post.deleted_at.is_(None))

        # Filter by status
        if status:
            stmt = stmt.where(Post.status == status)

        # Filter by platform (platforms JSON array contains the platform)
        if platform:
            # SQLite JSON query (simplified - may need adjustment for production)
            stmt = stmt.where(Post.platforms.like(f"%{platform}%"))

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = session.exec(count_stmt).one()

        # Apply pagination
        stmt = stmt.order_by(Post.created_at.desc()).limit(
            limit).offset(offset)

        # Execute query
        posts = session.exec(stmt).all()

        return {
            "posts": [
                {
                    "id": post.id,
                    "kind": post.kind,
                    "title": post.title,
                    "body": post.body,
                    "source_url": post.source_url,
                    "tags": post.tags,
                    "platforms": post.platforms,
                    "status": post.status,
                    "scheduled_at": post.scheduled_at.isoformat() if post.scheduled_at else None,
                    "published_at": post.published_at.isoformat() if post.published_at else None,
                    "created_at": post.created_at.isoformat() if post.created_at else None,
                    "updated_at": post.updated_at.isoformat() if post.updated_at else None,
                }
                for post in posts
            ],
            "total": total,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching queue: {str(e)}")


# ==================== Update Post ====================

@router.patch("/api/content/{post_id}")
async def update_post(
    post_id: int,
    data: Dict[str, Any] = Body(...),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Update a post."""
    try:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.deleted_at:
            raise HTTPException(status_code=400, detail="Post is deleted")

        # Update allowed fields
        allowed_fields = ["title", "body", "platforms", "scheduled_at", "tags"]
        for field in allowed_fields:
            if field in data:
                setattr(post, field, data[field])

        post.updated_at = datetime.utcnow()
        session.add(post)
        session.commit()
        session.refresh(post)

        return {
            "message": "Post updated successfully",
            "post": {
                "id": post.id,
                "kind": post.kind,
                "title": post.title,
                "body": post.body,
                "status": post.status,
                "platforms": post.platforms,
                "scheduled_at": post.scheduled_at.isoformat() if post.scheduled_at else None,
                "updated_at": post.updated_at.isoformat() if post.updated_at else None,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating post: {str(e)}")


# ==================== Approve Post ====================

@router.post("/api/content/{post_id}/approve")
async def approve_post(
    post_id: int,
    body_data: Dict[str, Any] = Body(...),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Approve a post and optionally schedule it."""
    try:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.deleted_at:
            raise HTTPException(status_code=400, detail="Post is deleted")

        schedule_immediately = body_data.get("schedule_immediately", False)

        # Update status
        post.status = "approved"

        # Set scheduled_at based on schedule_immediately flag
        if schedule_immediately:
            post.scheduled_at = datetime.utcnow()
        elif not post.scheduled_at:
            # Set default scheduled time (e.g., 1 hour from now)
            post.scheduled_at = datetime.utcnow() + timedelta(hours=1)

        post.updated_at = datetime.utcnow()
        session.add(post)
        session.commit()
        session.refresh(post)

        return {
            "message": "Post approved successfully",
            "scheduled_at": post.scheduled_at.isoformat() if post.scheduled_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error approving post: {str(e)}")


# ==================== Reject Post ====================

@router.post("/api/content/{post_id}/reject")
async def reject_post(
    post_id: int,
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Soft delete (reject) a post."""
    try:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.deleted_at:
            raise HTTPException(status_code=400, detail="Post already deleted")

        # Soft delete by setting deleted_at
        post.deleted_at = datetime.utcnow()
        post.updated_at = datetime.utcnow()
        session.add(post)
        session.commit()

        return {"message": "Post rejected (soft deleted) successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error rejecting post: {str(e)}")


# ==================== Delete Post ====================

@router.delete("/api/content/{post_id}")
async def delete_post(
    post_id: int,
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Hard delete a post."""
    try:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        session.delete(post)
        session.commit()

        return {"message": "Post deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting post: {str(e)}")


# ==================== Publish Post ====================

@router.post("/api/publish/{post_id}")
async def publish_post_endpoint(
    post_id: int,
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Publish a post immediately."""
    try:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.deleted_at:
            raise HTTPException(status_code=400, detail="Post is deleted")

        if post.status != "approved":
            raise HTTPException(
                status_code=400, detail=f"Post status must be 'approved', got '{post.status}'"
            )

        # Call publishing function
        result = await publishing.publish_post(post)

        return {
            "message": "Post published successfully",
            "result": result,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error publishing post: {str(e)}")
