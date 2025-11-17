from __future__ import annotations

from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Body
from openai import AsyncOpenAI
from sqlmodel import Session, select, func

from app.database import engine
from app.models import Post
from app import publishing
from app import video_generator
from app import content_scraper
from app import scheduler
from app import video_production
from app import video_competitor_exact
from app import schemas_news

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
        print("[api] GET /api/stats/dashboard called")
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
        print(f"[api] Error fetching dashboard stats: {str(e)}")
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
        print(
            f"[api] GET /api/content/queue called - status={status}, platform={platform}, limit={limit}, offset={offset}")
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

        # Get assets for video posts
        from app.models import Asset
        video_post_ids = [p.id for p in posts if p.kind == "video"]
        assets_map = {}
        if video_post_ids:
            assets_stmt = select(Asset).where(
                Asset.post_id.in_(video_post_ids),
                Asset.type == "video"
            )
            assets = session.exec(assets_stmt).all()
            for asset in assets:
                if asset.post_id not in assets_map:
                    assets_map[asset.post_id] = []
                assets_map[asset.post_id].append({
                    "id": asset.id,
                    "type": asset.type,
                    "path": asset.path,
                })

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
                    # Include video assets
                    "assets": assets_map.get(post.id, []),
                }
                for post in posts
            ],
            "total": total,
        }
    except Exception as e:
        print(f"[api] Error fetching queue: {str(e)}")
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
        print(f"[api] PATCH /api/content/{post_id} called")
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
    """Approve a text post and create a video post for it."""
    try:
        print(f"[api] POST /api/content/{post_id}/approve called")
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.deleted_at:
            raise HTTPException(status_code=400, detail="Post is deleted")

        # Update text post status to approved
        post.status = "approved"
        post.updated_at = datetime.utcnow()
        session.add(post)

        # If it's a text post, create a corresponding video post
        video_post_id = None
        if post.kind == "text":
            # Generate video script from the text post
            try:
                # removed per guardrails; use router
# # removed per guardrails; use router
# from openai import AsyncOpenAI
                client = AsyncOpenAI()

                prompt = (
                    f"Create a VIRAL video script (15-20 seconds) based on this social media post.\n\n"
                    f"Original post:\n{post.body}\n\n"
                    f"Title: {post.title}\n\n"
                    f"CRITICAL: Use viral hooks and make it engaging! Follow this EXACT format:\n\n"
                    f"Hook (0-1.5s): [ULTRA-ENGAGING opening - question, shocking statement, or curiosity gap]\n"
                    f"Main (2-8s): [main content - key message, value proposition]\n"
                    f"Why (9-15s): [why it matters - emotional impact, benefits, transformation]\n"
                    f"CTA (16-20s): [call to action - clear next step, engagement driver]\n\n"
                    f"Viral Hook Formulas to Consider:\n"
                    f"- Question: 'Did you know...?' or 'What if I told you...?'\n"
                    f"- Shocking: 'This will change everything...' or 'You won't believe...'\n"
                    f"- Curiosity Gap: 'The secret most people don't know...'\n"
                    f"- Pattern Interrupt: 'Stop doing X, start doing Y...'\n\n"
                    f"Return ONLY the script in the exact format above with timing labels."
                )

                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system",
                            "content": "You are an expert viral video script writer. You specialize in creating engaging, high-converting social media video scripts with powerful hooks. Always use the exact format: Hook (0-1.5s): ... Main (2-8s): ... Why (9-15s): ... CTA (16-20s): ..."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.8,  # Higher creativity for viral hooks
                )

                video_script = response.choices[
                    0].message.content or f"Hook: {post.body[:50]}...\nMain: {post.body}\nWhy: Important update\nCTA: Share your thoughts!"

                # Create video post
                video_post = Post(
                    kind="video",
                    title=post.title,
                    body=video_script.strip(),
                    source_url=post.source_url,
                    tags=post.tags,
                    platforms=[
                        "Instagram", "TikTok", "YouTube Shorts"] if not post.platforms else post.platforms,
                    status="video_production",  # Start video generation
                )
                session.add(video_post)
                session.commit()
                session.refresh(video_post)

                video_post_id = video_post.id
                print(
                    f"[api] Created video post {video_post_id} for text post {post_id}")

                # Now trigger video generation IMMEDIATELY
                print(
                    f"[api] Starting video generation for post {video_post_id}...")
                try:
                    video_result = await video_generator.generate_video_for_post(video_post)
                    print(
                        f"[api] ✅ Video generated successfully: {video_result.get('video_url', 'No URL')}")
                except Exception as video_error:
                    print(
                        f"[api] ❌ Video generation failed: {str(video_error)}")
                    import traceback
                    traceback.print_exc()
                    # Post stays in video_production status - will retry via scheduler
            except Exception as e:
                print(f"[api] Error generating video script: {str(e)}")
                import traceback
                traceback.print_exc()
                # Still approve the text post even if video generation fails
                session.commit()
        else:
            session.commit()
            session.refresh(post)

        return {
            "message": "Post approved successfully. Video creation started." if post.kind == "text" and video_post_id else "Post approved successfully",
            "video_post_id": video_post_id,
            "scheduled_at": post.scheduled_at.isoformat() if post.scheduled_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[api] Error approving post: {str(e)}")
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
        print(f"[api] POST /api/content/{post_id}/reject called")
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


# ==================== Clear All (Testing) ====================

@router.delete("/api/content/clear-all")
async def clear_all_posts() -> Dict[str, Any]:
    """Delete all posts and assets (FOR TESTING ONLY)"""
    from app.models import Asset

    with Session(engine) as session:
        # Delete all assets
        assets = session.exec(select(Asset)).all()
        for asset in assets:
            session.delete(asset)

        # Delete all posts
        posts = session.exec(select(Post)).all()
        for post in posts:
            session.delete(post)

        session.commit()

    return {"message": "All posts and assets deleted"}


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


# ==================== Generate Content ====================

@router.post("/api/content/generate")
async def generate_content(
    data: Dict[str, Any] = Body(...),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Generate new content manually."""
    try:
        print("[api] POST /api/content/generate called")

        # Extract parameters
        kind = data.get("kind", "text")  # text or video
        title = data.get("title", "")
        body = data.get("body", "")
        platforms = data.get("platforms", ["General"])
        tags = data.get("tags", [])

        if not title and not body:
            raise HTTPException(
                status_code=400, detail="title or body is required")

        # Create post
        post = Post(
            kind=kind,
            title=title or "Generated Post",
            body=body or title,
            platforms=platforms,
            tags=tags,
            status="draft",
        )

        session.add(post)
        session.commit()
        session.refresh(post)

        print(f"[api] Created post {post.id}")

        return {
            "message": "Content generated successfully",
            "post": {
                "id": post.id,
                "kind": post.kind,
                "title": post.title,
                "body": post.body,
                "status": post.status,
                "platforms": post.platforms,
                "created_at": post.created_at.isoformat() if post.created_at else None,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[api] Error generating content: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error generating content: {str(e)}")


@router.post("/api/content/generate-demo")
async def generate_demo_content(
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Generate 20 sample posts without calling external APIs."""
    try:
        print("[api] POST /api/content/generate-demo called")

        import random

        # Sample RSS-style articles for context
        sample_articles = [
            {
                "title": "AI Revolutionizes Healthcare Diagnostics",
                "summary": "New AI models can detect diseases faster than traditional methods.",
                "source": "TechCrunch AI",
            },
            {
                "title": "GPT-5 Expected to Launch Next Year",
                "summary": "Industry insiders predict major breakthroughs in reasoning capabilities.",
                "source": "OpenAI Blog",
            },
            {
                "title": "Machine Learning in Autonomous Vehicles",
                "summary": "Self-driving cars reach new safety milestones.",
                "source": "The Verge AI",
            },
            {
                "title": "Neural Networks for Climate Modeling",
                "summary": "AI helps scientists predict extreme weather patterns.",
                "source": "MIT Tech Review",
            },
            {
                "title": "DeepMind Solves Protein Folding Mystery",
                "summary": "Breakthrough in understanding protein structures.",
                "source": "DeepMind",
            },
        ]

        platforms_list = [
            ["LinkedIn"],
            ["Twitter"],
            ["Facebook"],
            ["Instagram"],
            ["YouTube"],
            ["LinkedIn", "Twitter"],
            ["Instagram", "TikTok"],
            ["Facebook", "LinkedIn"],
        ]

        viral_hooks = [
            "This will change everything...",
            "You won't believe what happened next",
            "Scientists just discovered something incredible",
            "This AI breakthrough is going viral",
            "The future of tech starts now",
            "Why everyone is talking about this",
            "The secret most people don't know",
            "This changes how we think about AI",
            "Breaking: Major tech announcement",
            "You need to see this",
        ]

        video_scripts = [
            "Hook: Did you know AI can now write code?\nMain: Recent advances show AI assistants creating full applications.\nWhy: This saves developers hours of work.\nCTA: What do you think? Comment below!",
            "Hook: This AI model is terrifying and amazing.\nMain: It generates photorealistic images in seconds.\nWhy: Content creation will never be the same.\nCTA: Follow for more tech updates!",
            "Hook: Scientists just broke another barrier.\nMain: AI can now predict weather 10x more accurately.\nWhy: This saves lives and resources.\nCTA: Share if you found this interesting!",
        ]

        # Diverse stock videos for demo content
        stock_videos = [
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
        ]

        created_posts = []

        # Create 10 text posts
        for i in range(10):
            article = random.choice(sample_articles)
            hook = random.choice(viral_hooks)

            post = Post(
                kind="text",
                title=article["title"],
                body=f"{hook}\n\n{article['summary']}\n\n#AI #Tech #Innovation",
                source_url=f"https://example.com/article-{i+1}",
                tags=[article["source"], "demo"],
                platforms=random.choice(platforms_list),
                status="draft",  # Always draft so they appear in Text Posts tab
            )
            session.add(post)
            created_posts.append(post)

        # Create 10 video posts
        for i in range(10):
            article = random.choice(sample_articles)
            script = random.choice(video_scripts)

            post = Post(
                kind="video",
                title=article["title"],
                body=script,
                source_url=f"https://example.com/video-{i+1}",
                tags=[article["source"], "demo", "video"],
                platforms=random.choice(
                    [["Instagram", "TikTok"], ["YouTube Shorts"], ["TikTok"]]),
                status="approved",  # Set to approved so they appear in Video Production tab
                video_duration=random.randint(15, 20),
                created_at=datetime.utcnow() - timedelta(hours=i+1),
                regeneration_count=0,
                total_cost=round(random.uniform(0.15, 0.40), 3)
            )
            session.add(post)
            session.flush()  # Flush to get the post ID

            # Add sample video asset for ALL video posts
            from app.models import Asset
            video_asset = Asset(
                post_id=post.id,
                type="video",
                # Rotate through different videos
                path=stock_videos[i % len(stock_videos)],
                created_at=datetime.utcnow()
            )
            session.add(video_asset)

            created_posts.append(post)

        session.commit()

        # Refresh all posts to get IDs
        for post in created_posts:
            session.refresh(post)

        print(f"[api] Created {len(created_posts)} demo posts")

        return {
            "message": f"Successfully created {len(created_posts)} demo posts",
            "count": len(created_posts),
            "posts": [
                {
                    "id": post.id,
                    "kind": post.kind,
                    "title": post.title,
                    "status": post.status,
                    "platforms": post.platforms,
                }
                for post in created_posts
            ],
        }
    except Exception as e:
        print(f"[api] Error generating demo content: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error generating demo content: {str(e)}")


# ==================== Approve Video ====================

@router.post("/api/content/{post_id}/approve-video")
async def approve_video(
    post_id: int,
    body_data: Dict[str, Any] = Body(...),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Approve a video post and trigger video generation."""
    try:
        print(f"[api] POST /api/content/{post_id}/approve-video called")

        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.deleted_at:
            raise HTTPException(status_code=400, detail="Post is deleted")

        if post.kind != "video":
            raise HTTPException(
                status_code=400, detail="Post must be a video post")

        schedule_immediately = body_data.get("schedule_immediately", False)

        # Update status - video posts go to video_production first
        post.status = "video_production"

        # Set scheduled_at based on schedule_immediately flag
        if schedule_immediately:
            post.scheduled_at = datetime.utcnow()
        elif not post.scheduled_at:
            # Set default scheduled time (e.g., 2 hours from now for video processing)
            post.scheduled_at = datetime.utcnow() + timedelta(hours=2)

        post.updated_at = datetime.utcnow()
        session.add(post)
        session.commit()
        session.refresh(post)

        print(f"[api] Video post {post_id} approved, status: {post.status}")

        return {
            "message": "Video post approved and queued for production",
            "status": post.status,
            "scheduled_at": post.scheduled_at.isoformat() if post.scheduled_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[api] Error approving video: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error approving video: {str(e)}")


# ==================== Regenerate Content ====================

@router.post("/api/content/{post_id}/regenerate-text")
async def regenerate_text(
    post_id: int,
    body_data: Dict[str, Any] = Body(default={}),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Regenerate text variants for a post."""
    try:
        print(f"[api] POST /api/content/{post_id}/regenerate-text called")
        print(f"[api] Body data: {body_data}")

        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.deleted_at:
            raise HTTPException(status_code=400, detail="Post is deleted")

        # Extract options - handle both camelCase and snake_case
        num_variants = body_data.get(
            "variantCount") or body_data.get("num_variants", 3)
        custom_instructions = body_data.get(
            "customInstructions") or body_data.get("custom_instructions", "")
        change_hook_style = body_data.get(
            "changeHookStyle") or body_data.get("change_hook_style", False)
        change_tone = body_data.get(
            "changeTone") or body_data.get("change_tone", False)

        # Import OpenAI client
        try:
            # removed per guardrails; use router
# # removed per guardrails; use router
# from openai import AsyncOpenAI
            client = AsyncOpenAI()
        except ImportError:
            raise HTTPException(
                status_code=500, detail="OpenAI client not available")

        # Build prompt based on options
        instructions = []
        if change_hook_style:
            instructions.append(
                "try a different hook style (question, statement, story, etc.)")
        if change_tone:
            instructions.append(
                "change the tone (more casual, formal, enthusiastic, etc.)")
        if custom_instructions:
            instructions.append(custom_instructions)

        instruction_text = ". ".join(
            instructions) if instructions else "improve the content"

        prompt = (
            f"Generate {num_variants} improved variants of this social media post.\n"
            f"Original post:\n{post.body}\n\n"
            f"Requirements: {instruction_text}.\n"
            f"Keep the core message and context the same. "
            f"Make each variant unique but on-topic.\n"
            f"Return ONLY a JSON array of strings, each string is one variant post."
        )

        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a social media copywriter. Return only valid JSON arrays."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
            )

            content = response.choices[0].message.content or "[]"
            import json
            variants = json.loads(content)

            if not isinstance(variants, list) or len(variants) == 0:
                raise ValueError("Invalid response format")

            # Update the post with the first variant (best one)
            post.body = variants[0]
            post.updated_at = datetime.utcnow()
            session.add(post)
            session.commit()
            session.refresh(post)

            print(
                f"[api] Generated {len(variants)} text variants for post {post_id}, updated post")

            return {
                "message": f"Generated {len(variants)} text variants and updated post",
                "variants": variants,
                "post_id": post_id,
                "updated_post": {
                    "id": post.id,
                    "body": post.body,
                    "status": post.status,
                }
            }
        except Exception as e:
            print(f"[api] OpenAI error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to generate variants: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        print(f"[api] Error regenerating text: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error regenerating text: {str(e)}")


@router.post("/api/content/{post_id}/regenerate-video")
async def regenerate_video(
    post_id: int,
    body_data: Dict[str, Any] = Body(default={}),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Regenerate video script for a post, preserving context."""
    try:
        print(f"[api] POST /api/content/{post_id}/regenerate-video called")
        print(f"[api] Body data: {body_data}")

        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.deleted_at:
            raise HTTPException(status_code=400, detail="Post is deleted")

        if post.kind != "video":
            raise HTTPException(
                status_code=400, detail="Post must be a video post")

        # Extract options - handle both camelCase and snake_case
        custom_instructions = body_data.get(
            "customInstructions") or body_data.get("custom_instructions", "")
        change_hook_style = body_data.get(
            "changeHookStyle") or body_data.get("change_hook_style", False)
        change_tone = body_data.get(
            "changeTone") or body_data.get("change_tone", False)

        # Import OpenAI client
        try:
            # removed per guardrails; use router
# # removed per guardrails; use router
# from openai import AsyncOpenAI
            client = AsyncOpenAI()
        except ImportError:
            raise HTTPException(
                status_code=500, detail="OpenAI client not available")

        # Build prompt that preserves script context
        instructions = []
        if change_hook_style:
            instructions.append("try a different hook style")
        if change_tone:
            instructions.append("change the tone")
        if custom_instructions:
            instructions.append(custom_instructions)

        instruction_text = ". ".join(
            instructions) if instructions else "improve the script"

        # Preserve the script structure and context
        prompt = (
            f"Regenerate this video script with improvements while keeping the EXACT same context and topic.\n\n"
            f"Current script:\n{post.body}\n\n"
            f"Title: {post.title}\n"
            f"Source: {post.source_url or 'N/A'}\n\n"
            f"Requirements: {instruction_text}.\n"
            f"CRITICAL: Keep the same topic, message, and context. Only improve the delivery.\n"
            f"Format: Hook (0-1.5s), Main (2-8s), Why (9-15s), CTA (16-20s).\n"
            f"Return the improved script as a single string matching the same format."
        )

        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a video script writer. Return only the improved script text, maintaining the same structure and context."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,  # Lower temperature to maintain context better
            )

            new_script = response.choices[0].message.content or post.body

            # Update the post with the regenerated script
            post.body = new_script.strip()
            post.status = "video_production"  # Reset to production - will regenerate video
            post.updated_at = datetime.utcnow()
            session.add(post)
            session.commit()
            session.refresh(post)

            # Video regeneration will be processed by scheduler
            print(
                f"[api] Video regeneration queued for post {post_id} (status: video_production)")

            print(
                f"[api] Regenerated video script for post {post_id}, preserved context")

            return {
                "message": "Video script regenerated successfully, video generation started",
                "status": post.status,
                "post_id": post_id,
                "updated_post": {
                    "id": post.id,
                    "body": post.body,
                    "title": post.title,
                    "status": post.status,
                }
            }
        except Exception as e:
            print(f"[api] OpenAI error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to regenerate script: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        print(f"[api] Error regenerating video: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error regenerating video: {str(e)}")


# ==================== Get Versions ====================

@router.get("/api/content/{post_id}/versions")
async def get_versions(
    post_id: int,
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Get regeneration history for a post."""
    try:
        print(f"[api] GET /api/content/{post_id}/versions called")

        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.deleted_at:
            raise HTTPException(status_code=400, detail="Post is deleted")

        # For now, return current version as history
        # In production, this would query a versions table
        versions = [
            {
                "version": 1,
                "body": post.body,
                "created_at": post.created_at.isoformat() if post.created_at else None,
                "updated_at": post.updated_at.isoformat() if post.updated_at else None,
            }
        ]

        print(f"[api] Retrieved {len(versions)} versions for post {post_id}")

        return {
            "post_id": post_id,
            "versions": versions,
            "current_version": 1,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[api] Error fetching versions: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching versions: {str(e)}")


# ==================== Video Generation ====================

@router.get("/api/content/{post_id}/video-status")
async def get_video_status(
    post_id: int,
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Get video generation status for a post."""
    try:
        print(f"[api] GET /api/content/{post_id}/video-status called")

        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.kind != "video":
            raise HTTPException(
                status_code=400, detail="Post must be a video post")

        # Get video assets
        from app.models import Asset
        stmt = select(Asset).where(Asset.post_id ==
                                   post_id, Asset.type == "video")
        assets = session.exec(stmt).all()

        return {
            "post_id": post_id,
            "status": post.status,
            "has_video": len(assets) > 0,
            "video_url": assets[0].path if assets else None,
            "asset_id": assets[0].id if assets else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[api] Error fetching video status: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching video status: {str(e)}")


@router.post("/api/content/{post_id}/generate-video")
async def trigger_video_generation(
    post_id: int,
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Manually trigger video generation for a post."""
    try:
        print(f"[api] POST /api/content/{post_id}/generate-video called")

        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.kind != "video":
            raise HTTPException(
                status_code=400, detail="Post must be a video post")

        # Update status to video_production
        post.status = "video_production"
        session.add(post)
        session.commit()
        session.refresh(post)

        # Video generation will be processed by scheduler automatically
        # Status is set to video_production, scheduler will process it
        print(
            f"[api] Video generation queued for post {post_id} (status: video_production)")

        return {
            "message": "Video generation started",
            "status": post.status,
            "post_id": post_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[api] Error triggering video generation: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error triggering video generation: {str(e)}")


# ==================== Publish Post ====================

@router.post("/api/publish/{post_id}")
async def publish_post_endpoint(
    post_id: int,
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Publish a post immediately."""
    try:
        print(f"[api] POST /api/publish/{post_id} called")

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

        print(f"[api] Post {post_id} published successfully")

        return {
            "message": "Post published successfully",
            "result": result,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[api] Error publishing post: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error publishing post: {str(e)}")


# ==================== Debug Endpoint ====================

@router.get("/api/debug/posts")
async def debug_posts() -> Dict[str, Any]:
    """Debug endpoint to see all posts and their assets"""
    from app.models import Asset

    with Session(engine) as session:
        posts = session.exec(select(Post)).all()

        result = []
        for post in posts:
            assets = session.exec(
                select(Asset).where(Asset.post_id == post.id)
            ).all()

            result.append({
                "id": post.id,
                "title": post.title,
                "kind": post.kind,
                "status": post.status,
                "has_assets": len(assets) > 0,
                "assets": [
                    {
                        "type": a.type,
                        "path": a.path
                    } for a in assets
                ]
            })

        return {
            "total_posts": len(posts),
            "posts": result
        }


# ==================== TEST VIDEO GENERATION (COMPETITOR STYLE) ====================

@router.post("/api/video/competitor-test/{post_id}")
async def test_competitor_style_video(post_id: int):
    import traceback
    import os
    from app.models import Post
    from app.database import engine

    print("\n" + "="*80)
    print(f"🎬 COMPETITOR VIDEO TEST STARTED - Post ID: {post_id}")
    print("="*80)

    try:
        # Step 1: Get post
        print(f"\n[STEP 1] Fetching post {post_id} from database...")
        with Session(engine) as session:
            post = session.get(Post, post_id)
            if not post:
                print(f"❌ ERROR: Post {post_id} not found in database")
                raise HTTPException(status_code=404, detail="Post not found")
            print(f"✅ Post found: {post.title}")
            print(f"   - Kind: {post.kind}")
            print(f"   - Status: {post.status}")
            print(f"   - Body length: {len(post.body)} chars")

        # Step 2: Check dependencies
        print("\n[STEP 2] Checking dependencies...")
        try:
            from moviepy.editor import ImageClip, concatenate_videoclips
            import numpy as np
            from PIL import Image, ImageDraw, ImageFont
            print("✅ MoviePy and PIL imported")
        except Exception as e:
            print(f"❌ Import failed: {e}")
            raise HTTPException(
                status_code=500, detail=f"Dependencies not installed: {e}")

        try:
            print("✅ Requests imported")
        except Exception as e:
            print(f"❌ Requests import failed: {e}")
            raise HTTPException(
                status_code=500, detail=f"Requests not installed: {e}")

        # Step 3: Check Pexels API key
        print("\n[STEP 3] Checking Pexels API key...")
        pexels_key = os.getenv("PEXELS_API_KEY", "")
        if pexels_key:
            print(f"✅ Pexels key found: {pexels_key[:10]}...")
        else:
            print("⚠️ WARNING: No Pexels API key - will use fallback colors")

        # Step 4: Define helper functions for PIL text rendering
        def _load_bold_font(fontsize: int) -> ImageFont.FreeTypeFont:
            """Load a bold font, trying multiple common paths."""
            font_paths = [
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                "/Library/Fonts/Arial Bold.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Supplemental/Impact.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "C:\\Windows\\Fonts\\arialbd.ttf",
            ]
            for path in font_paths:
                if os.path.exists(path):
                    try:
                        return ImageFont.truetype(path, fontsize)
                    except Exception:
                        continue
            try:
                return ImageFont.load_default()
            except Exception:
                return ImageFont.load_default()

        def create_text_image_pil(text: str, fontsize: int, color: str, stroke_color: str, stroke_width: int, size=(1080, 1920), max_width=900):
            """Create text image using PIL (no ImageMagick required)."""
            print(f"    DEBUG: Creating text image with size {size}")
            img = Image.new('RGBA', size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            font = _load_bold_font(fontsize)
            print(f"    DEBUG: Font loaded: {type(font)}")

            # Handle multi-line text wrapping
            words = text.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                test_width = bbox[2] - bbox[0]
                if test_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            # Calculate total height
            line_heights = []
            line_widths = []
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_widths.append(bbox[2] - bbox[0])
                line_heights.append(bbox[3] - bbox[1])

            total_height = sum(line_heights) + (len(lines) - 1) * 20
            start_y = (size[1] - total_height) // 2

            # Draw each line
            current_y = start_y
            for line, line_width, line_height in zip(lines, line_widths, line_heights):
                x = (size[0] - line_width) // 2
                if stroke_width > 0:
                    for adj_x in range(-stroke_width, stroke_width + 1):
                        for adj_y in range(-stroke_width, stroke_width + 1):
                            draw.text((x + adj_x, current_y + adj_y), line, font=font, fill=stroke_color)
                draw.text((x, current_y), line, font=font, fill=color)
                current_y += line_height + 20

            # Return RGBA image (MoviePy's ImageClip handles transparency correctly)
            print(f"    DEBUG: Final image mode: {img.mode}, size: {img.size}")
            return img  # Keep RGBA for transparency

        # Step 5: Create scenes
        print("\n[STEP 4] Creating scene structure...")
        SCENES = [
            {"duration": 6, "text": "🚨 BREAKING NEWS", "color": "#000000",
                "size": 100, "keywords": ["ai", "technology"]},  # Black text on yellow bg
            {"duration": 6, "text": post.title[:50], "color": "#FFFFFF", "size": 60, "keywords": [
                "developer", "coding"]},  # White text on blue bg
            {"duration": 6, "text": "KEY DETAILS", "color": "#000000",
                "size": 90, "keywords": ["artificial intelligence"]},  # Black text on green bg
            {"duration": 6, "text": "WHY THIS MATTERS", "color": "#FFFFFF",
                "size": 70, "keywords": ["business tech"]},  # White text on red bg
            {"duration": 6, "text": "FOLLOW @XSELLER.AI",
                "color": "#000000", "size": 65, "keywords": ["social media"]}  # Black text on white bg
        ]
        print(f"✅ Created {len(SCENES)} scenes")

        # Step 5: Generate clips
        print("\n[STEP 5] Generating video clips...")
        clips = []
        # Vibrant colors matching competitor videos (bright, eye-catching)
        colors = ['#FFFF00', '#0066FF', '#00FF00', '#FF0000', '#FFFFFF']  # Yellow, Blue, Green, Red, White

        for i, scene in enumerate(SCENES):
            print(f"\n  Scene {i+1}/{len(SCENES)}: {scene['text']}")

            try:
                # Create text using PIL (no ImageMagick needed)
                print(f"    - Creating text on {colors[i]} background...")
                text_img = create_text_image_pil(
                    text=scene["text"],
                    fontsize=scene["size"],
                    color=scene["color"],
                    stroke_color='black',
                    stroke_width=5,
                    size=(1080, 1920),  # PIL format: (width, height)
                    max_width=900
                )

                # Convert RGBA text image to RGB by compositing over the background color
                text_array = np.array(text_img)
                print(f"    DEBUG: PIL image size: {text_img.size}, numpy array shape: {text_array.shape}")

                # Create RGB image by compositing RGBA text over the colored background
                if text_array.shape[2] == 4:  # RGBA
                    # Get background color for this scene
                    hex_color = colors[i].lstrip('#')
                    bg_color = tuple(int(hex_color[j:j+2], 16) for j in (0, 2, 4))
                    print(f"    DEBUG: Hex {colors[i]} -> RGB {bg_color}")

                    # Create RGB background
                    rgb_img = np.ones((text_array.shape[0], text_array.shape[1], 3), dtype=np.uint8)
                    rgb_img[:, :] = bg_color

                    # Alpha composite: result = foreground * alpha + background * (1 - alpha)
                    alpha = text_array[:, :, 3:4] / 255.0  # Normalize alpha to 0-1
                    foreground = text_array[:, :, :3]
                    rgb_img = (foreground * alpha + rgb_img * (1 - alpha)).astype(np.uint8)

                    scene_clip = ImageClip(rgb_img).set_duration(scene["duration"])
                    print(f"    ✅ Scene created: text composited onto {colors[i]} background")
                else:
                    scene_clip = ImageClip(text_array).set_duration(scene["duration"])

                clips.append(scene_clip)
                print(f"    ✅ Scene {i+1} complete: {scene_clip.size}, {scene_clip.duration}s")

            except Exception as e:
                print(f"    ❌ Scene {i+1} FAILED: {e}")
                print(f"    Traceback: {traceback.format_exc()}")
                raise

        # Step 6: Concatenate
        print(f"\n[STEP 6] Concatenating {len(clips)} clips...")
        for i, clip in enumerate(clips):
            try:
                frame = clip.get_frame(0)
                print(f"   Clip {i+1}: size={clip.size}, duration={clip.duration}s, frame shape={frame.shape}")
            except Exception as e:
                print(f"   Clip {i+1}: ERROR getting frame - {e}")
        try:
            final = concatenate_videoclips(clips, method="compose")
            print(f"✅ Final video: {final.size}, {final.duration}s")
        except Exception as e:
            print(f"❌ Concatenation FAILED: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            raise

        # Step 7: Generate TTS voiceover
        print("\n[STEP 7] Generating TTS voiceover...")
        audio_path = None
        try:
            from app import tts_service

            # Create narration from post content
            narration_text = f"{post.title}. {post.body[:500]}"
            print(f"   Generating voiceover for: {narration_text[:100]}...")

            # Check if user has selected a voice and energy mode
            selected_voice = "charlotte"  # Default: British female professional voice
            selected_energy = "professional"  # Default energy mode

            if post.extra_data and "selected_voice" in post.extra_data:
                selected_voice = post.extra_data["selected_voice"]
                print(f"   Using user-selected voice: {selected_voice}")
            else:
                print(f"   Using default voice: {selected_voice}")

            if post.extra_data and "voice_energy" in post.extra_data:
                selected_energy = post.extra_data["voice_energy"]
                print(f"   Using user-selected energy: {selected_energy}")
            else:
                print(f"   Using default energy: {selected_energy}")

            audio_path = await tts_service.generate_voiceover(
                text=narration_text,
                provider="auto",  # Will try ElevenLabs -> OpenAI -> gTTS
                voice=selected_voice,
                energy=selected_energy
            )

            if audio_path:
                print(f"✅ Voiceover generated: {audio_path}")
            else:
                print("⚠️ Voiceover generation skipped (no provider available)")
        except Exception as e:
            print(f"⚠️ Warning: Voiceover generation failed: {e}")
            import traceback
            traceback.print_exc()
            audio_path = None

        # Step 8: Add audio to video if available
        if audio_path and os.path.exists(audio_path):
            print("\n[STEP 8] Adding audio to video...")
            try:
                from moviepy.editor import AudioFileClip
                audio_clip = AudioFileClip(audio_path)

                # Match audio duration to video or vice versa
                if audio_clip.duration > final.duration:
                    print(f"   Trimming audio from {audio_clip.duration}s to {final.duration}s")
                    audio_clip = audio_clip.subclip(0, final.duration)
                elif audio_clip.duration < final.duration:
                    print(f"   Video duration ({final.duration}s) > audio duration ({audio_clip.duration}s)")
                    print("   Trimming video to match audio")
                    final = final.subclip(0, audio_clip.duration)

                final = final.set_audio(audio_clip)
                print(f"✅ Audio synced to video ({audio_clip.duration}s)")
            except Exception as e:
                print(f"⚠️ Warning: Could not add audio: {e}")
                import traceback
                traceback.print_exc()

        # Step 9: Export
        print("\n[STEP 9] Exporting video...")
        try:
            # Create output directory relative to backend root
            output_dir = os.path.join(os.path.dirname(
                os.path.dirname(__file__)), "output", "test_videos")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(
                output_dir, f"competitor_test_{post_id}.mp4")
            print(f"   Output directory: {output_dir}")
            print(f"   Output path: {output_path}")
            print(f"   Has audio: {final.audio is not None}")

            final.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio=True if final.audio is not None else False,
                preset='medium',
                threads=2,
                logger='bar',
                ffmpeg_params=[
                    '-pix_fmt', 'yuv420p',  # Browser-compatible pixel format
                    '-profile:v', 'baseline',  # H.264 baseline profile (most compatible)
                    '-level', '3.0',  # H.264 level 3.0
                    '-movflags', '+faststart'  # Enable streaming (move moov atom to beginning)
                ]
            )
            print("✅ Export complete!")
        except Exception as e:
            print(f"❌ Export FAILED: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            raise

        print("\n" + "="*80)
        print("🎉 SUCCESS - Video generated!")
        print("="*80 + "\n")

        # Step 10: Update database with video path
        print("\n[STEP 10] Updating database with video asset...")
        try:
            # Store relative path from output directory for serving via /output route
            relative_video_path = f"test_videos/competitor_test_{post_id}.mp4"
            print(f"   Relative video path for database: {relative_video_path}")

            from app.models import Asset
            with Session(engine) as session:
                # Check if video asset already exists for this post
                existing_asset = session.exec(
                    select(Asset).where(
                        Asset.post_id == post_id,
                        Asset.type == "video"
                    )
                ).first()

                if existing_asset:
                    print(f"   Found existing video asset (id={existing_asset.id}), updating path...")
                    existing_asset.path = relative_video_path
                    session.add(existing_asset)
                else:
                    print("   No existing video asset, creating new one...")
                    new_asset = Asset(
                        post_id=post_id,
                        type="video",
                        path=relative_video_path
                    )
                    session.add(new_asset)

                session.commit()
                print(f"✅ Database updated with video path: {output_path}")
        except Exception as e:
            print(f"⚠️ WARNING: Failed to update database: {e}")
            print(f"   Video still saved at: {output_path}")

        return {
            "success": True,
            "video_path": output_path,
            "post_id": post_id,
            "duration": 30,
            "message": "Test video generated successfully and database updated"
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"\n{'='*80}")
        print("💥 FATAL ERROR in competitor-test endpoint")
        print(f"{'='*80}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nFull traceback:")
        print(traceback.format_exc())
        print(f"{'='*80}\n")

        raise HTTPException(
            status_code=500, detail=f"Video generation failed: {str(e)}")

# ==================== END TEST CODE ====================


# ==================== CONTENT SCRAPING TEST ====================

@router.get("/api/test/scrape")
async def test_scraping() -> Dict[str, Any]:
    """Test endpoint to manually trigger content scraping and see results."""
    try:
        print("\n" + "="*80)
        print("🧪 TESTING CONTENT SCRAPING")
        print("="*80)

        # Fetch content
        articles = await content_scraper.fetch_all_content()

        print(f"\n✅ Successfully fetched {len(articles)} articles")

        return {
            "success": True,
            "total_articles": len(articles),
            "articles": [
                {
                    "title": a.get("title", ""),
                    "source": a.get("source", ""),
                    "url": a.get("url", ""),
                    "summary": a.get("summary", "")[:200] + "...",
                    "published": a.get("published").isoformat() if a.get("published") else None,
                }
                for a in articles[:10]  # Return top 10 for preview
            ]
        }
    except Exception as e:
        print(f"❌ Scraping test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@router.post("/api/test/generate-from-scraping")
async def test_generate_from_scraping(
    limit: int = Query(3, ge=1, le=10),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Test endpoint to scrape content and generate posts."""
    try:
        print("\n" + "="*80)
        print("🧪 TESTING FULL CONTENT GENERATION PIPELINE")
        print("="*80)

        # Trigger the scheduler function manually
        await scheduler.fetch_and_generate_content()

        # Get recently created posts
        stmt = select(Post).where(
            Post.deleted_at.is_(None)
        ).order_by(Post.created_at.desc()).limit(limit * 2)

        posts = session.exec(stmt).all()

        return {
            "success": True,
            "message": "Content generation completed. Check recent posts.",
            "recent_posts_count": len(posts),
            "recent_posts": [
                {
                    "id": p.id,
                    "kind": p.kind,
                    "title": p.title,
                    "body": p.body[:200] + "...",
                    "status": p.status,
                    "source": p.source_url,
                }
                for p in posts[:10]
            ]
        }
    except Exception as e:
        print(f"❌ Generation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


# ==================== END SCRAPING TEST ====================


# ==================== NEW VIDEO GENERATION SYSTEM ====================

@router.post("/api/video/generate-pro/{post_id}")
async def generate_professional_video(
    post_id: int,
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Generate professional competitor-style video from post script.

    Uses scene-by-scene rendering with:
    - Text overlays with animations
    - Stock footage backgrounds (Pexels)
    - Proper timing and transitions
    """
    try:
        print(f"\n{'='*80}")
        print(f"🎬 GENERATING PROFESSIONAL VIDEO FOR POST {post_id}")
        print(f"{'='*80}\n")

        # Get post
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.kind != "video":
            raise HTTPException(status_code=400, detail="Post is not a video type")

        # Get script
        script = post.body
        if not script:
            raise HTTPException(status_code=400, detail="Post has no script")

        # Generate video
        result = await video_production.generate_video_from_script(
            script=script,
            title=post.title or "Untitled"
        )

        if result.get("success"):
            return {
                "success": True,
                "message": "Video generated successfully!",
                "video_path": result["video_path"],
                "duration": result.get("duration"),
                "scenes": result.get("scenes"),
                "post_id": post_id,
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Video generation failed: {result.get('error', 'Unknown error')}"
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")


@router.post("/api/video/generate-test")
async def test_video_generation(
    script: str = Body(..., embed=True),
    title: str = Body("Test Video", embed=True)
) -> Dict[str, Any]:
    """
    Test endpoint to generate video from custom script.

    Example request body:
    {
        "script": "Hook (0-2s): Did you know AI can now...\nMain (3-10s): Here's what's happening...",
        "title": "My Test Video"
    }
    """
    try:
        print(f"\n{'='*80}")
        print("🧪 TESTING VIDEO GENERATION")
        print(f"{'='*80}\n")

        result = await video_production.generate_video_from_script(
            script=script,
            title=title
        )

        if result.get("success"):
            return {
                "success": True,
                "message": "Test video generated successfully!",
                "video_path": result["video_path"],
                "duration": result.get("duration"),
                "scenes": result.get("scenes"),
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Video generation failed: {result.get('error', 'Unknown error')}"
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")


# ==================== END NEW VIDEO GENERATION ====================


# ==================== COMPETITOR-EXACT VIDEO (30s Viral Style) ====================

@router.post("/api/video/competitor/{post_id}")
async def generate_competitor_exact_video(
    post_id: int,
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Generate EXACT competitor-style 30s video from post.

    Matches viral tech shorts structure:
    0-3s: Hook (Question + shocking visual)
    3-9s: Demo (Tool showcase)
    9-18s: Proof (Before/after + stats)
    18-24s: Impact (Transformation message)
    24-30s: CTA (Link in bio)

    Uses 100% relevant stock footage based on script keywords.
    """
    try:
        print(f"\n{'='*80}")
        print(f"🎬 COMPETITOR-EXACT VIDEO GENERATION FOR POST {post_id}")
        print(f"{'='*80}\n")

        # Get post
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.kind != "video":
            raise HTTPException(status_code=400, detail="Post is not a video type")

        # Get script
        script = post.body
        if not script:
            raise HTTPException(status_code=400, detail="Post has no script")

        # Generate competitor-style video
        result = await video_competitor_exact.generate_exact_competitor_video(
            script=script,
            title=post.title or "AI News",
            add_voiceover=True
        )

        if result.get("success"):
            return {
                "success": True,
                "message": "Competitor-style video generated!",
                "video_path": result["video_path"],
                "duration": 30,
                "structure": "Hook/Demo/Proof/Impact/CTA",
                "post_id": post_id,
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Video generation failed: {result.get('error', 'Unknown error')}"
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")


@router.post("/api/video/competitor-test")
async def test_competitor_video(
    script: str = Body(..., embed=True),
    title: str = Body("AI Innovation", embed=True)
) -> Dict[str, Any]:
    """
    Test COMPETITOR-EXACT 30s video generation with custom script.

    Example script format:
    {
        "title": "GPT-4 Vision API Released",
        "script": "Hook: Can AI see and understand images now?\\n\\nDemo: OpenAI just released GPT-4 Vision API\\n\\nProof: 10X faster than competitors. 95% accuracy rate.\\n\\nImpact: This changes everything for developers\\n\\nCTA: Link in bio for full tutorial. Follow for daily AI updates"
    }
    """
    try:
        print(f"\n{'='*80}")
        print("🧪 TESTING COMPETITOR VIDEO GENERATION")
        print(f"Title: {title}")
        print(f"{'='*80}\n")

        result = await video_competitor_exact.generate_exact_competitor_video(
            script=script,
            title=title,
            add_voiceover=True
        )

        if result.get("success"):
            return {
                "success": True,
                "message": "Competitor-style test video generated!",
                "video_path": result["video_path"],
                "duration": 30,
                "structure": "Hook/Demo/Proof/Impact/CTA",
                "scenes": 5,
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Video generation failed: {result.get('error', 'Unknown error')}"
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")


# ==================== END COMPETITOR-EXACT VIDEO ====================


# ==================== VOICE SELECTION SYSTEM ====================

@router.post("/api/voice/analyze/{post_id}")
async def analyze_voice_for_post(
    post_id: int,
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Analyze post script and recommend voices based on content style.

    Returns:
        - style_analysis: Detected content type and recommended characteristics
        - recommended_voices: Top voices sorted by relevance score
    """
    try:
        # Get post
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Create narration text from post
        narration_text = f"{post.title}. {post.body[:500]}"

        # Import voice selector
        from app import voice_selector

        # Analyze script
        style_analysis = voice_selector.analyze_script_style(narration_text)

        # Get recommendations
        recommendations = voice_selector.get_voice_recommendations(narration_text)

        return {
            "post_id": post_id,
            "script_preview": narration_text[:200] + "...",
            "style_analysis": style_analysis,
            "recommended_voices": recommendations[:6],  # Top 6
            "total_voices": len(recommendations)
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Voice analysis error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Voice analysis failed: {str(e)}")


@router.post("/api/voice/preview/{post_id}")
async def generate_voice_previews(
    post_id: int,
    session: Session = Depends(get_session),
    voices: List[str] = Body(..., description="List of voice keys to generate previews for")
) -> Dict[str, Any]:
    """
    Generate preview audio files for selected voices.

    Args:
        post_id: ID of the post to use for preview text
        voices: List of voice keys to generate previews for (default: adam, joseph, antoni)

    Returns:
        Dictionary mapping voice names to preview file URLs
    """
    try:
        # Get post
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Create narration text (use first 100 words for preview)
        narration_text = f"{post.title}. {post.body}"
        words = narration_text.split()[:100]
        sample_text = " ".join(words)

        # Import voice selector
        from app import voice_selector

        # Generate previews
        previews = {}
        for voice_key in voices:
            if voice_key not in voice_selector.RECOMMENDED_VOICES:
                print(f"⚠️  Voice '{voice_key}' not found, skipping...")
                continue

            voice_info = voice_selector.RECOMMENDED_VOICES[voice_key]
            preview_path = await voice_selector.generate_voice_preview(
                voice_id=voice_info['id'],
                voice_name=voice_info['name'],
                sample_text=sample_text
            )

            if preview_path:
                # Convert absolute path to relative URL
                # e.g., /Users/.../backend/output/voice_previews/preview_adam.mp3
                # -> /api/voice/preview-file/preview_adam.mp3
                filename = os.path.basename(preview_path)
                preview_url = f"/api/voice/preview-file/{filename}"

                previews[voice_key] = {
                    "name": voice_info['name'],
                    "gender": voice_info['gender'],
                    "accent": voice_info['accent'],
                    "style": voice_info['style'],
                    "use_case": voice_info['use_case'],
                    "preview_url": preview_url,
                    "preview_path": preview_path
                }

        return {
            "post_id": post_id,
            "sample_text": sample_text[:150] + "...",
            "previews": previews,
            "count": len(previews)
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Voice preview generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Preview generation failed: {str(e)}")


@router.get("/api/voice/preview-file/{filename}")
async def serve_voice_preview(filename: str):
    """
    Serve voice preview audio files.
    """
    try:
        preview_dir = Path(__file__).parent.parent / "output" / "voice_previews"
        file_path = preview_dir / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Preview file not found")

        from fastapi.responses import FileResponse
        return FileResponse(
            path=str(file_path),
            media_type="audio/mpeg",
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File serving failed: {str(e)}")


@router.post("/api/voice/select/{post_id}")
async def save_voice_selection(
    post_id: int,
    voice_key: str = Body(..., embed=True),
    energy: Optional[str] = Body("professional", embed=True),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Save user's voice selection and energy mode for a post.

    This will be used in the final video generation.

    Args:
        post_id: Post ID
        voice_key: Voice identifier (e.g., "charlotte", "fable")
        energy: Energy mode - "professional", "energetic", or "viral"
    """
    try:
        # Get post
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Validate voice key
        from app import voice_selector
        if voice_key not in voice_selector.RECOMMENDED_VOICES:
            raise HTTPException(status_code=400, detail=f"Invalid voice key: {voice_key}")

        # Validate energy mode
        from app import tts_service
        if energy and energy not in tts_service.VOICE_ENERGY_PRESETS:
            raise HTTPException(status_code=400, detail=f"Invalid energy mode: {energy}. Must be one of: {list(tts_service.VOICE_ENERGY_PRESETS.keys())}")

        # Store voice selection in post extra_data
        if not post.extra_data:
            post.extra_data = {}

        post.extra_data["selected_voice"] = voice_key
        post.extra_data["voice_energy"] = energy or "professional"
        session.add(post)
        session.commit()
        session.refresh(post)

        voice_info = voice_selector.RECOMMENDED_VOICES[voice_key]
        energy_info = tts_service.VOICE_ENERGY_PRESETS.get(energy or "professional", {})

        return {
            "post_id": post_id,
            "selected_voice": voice_key,
            "voice_energy": energy,
            "voice_info": voice_info,
            "energy_info": energy_info,
            "message": f"Voice '{voice_info['name']}' with {energy} energy selected successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Voice selection error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Voice selection failed: {str(e)}")


@router.get("/api/voice/available")
async def get_available_voices() -> Dict[str, Any]:
    """
    Get all available voices with their details.
    """
    try:
        from app import voice_selector

        return {
            "voices": voice_selector.RECOMMENDED_VOICES,
            "count": len(voice_selector.RECOMMENDED_VOICES)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get voices: {str(e)}")


@router.get("/api/voice/energy-modes")
async def get_energy_modes() -> Dict[str, Any]:
    """
    Get all available voice energy modes with their settings.

    Returns:
        Dictionary with energy mode presets and their descriptions
    """
    try:
        from app import tts_service

        return {
            "energy_modes": tts_service.VOICE_ENERGY_PRESETS,
            "default": tts_service.DEFAULT_ENERGY,
            "count": len(tts_service.VOICE_ENERGY_PRESETS)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get energy modes: {str(e)}")


# ==================== END VOICE SELECTION SYSTEM ====================


# ==================== NEWS INGESTION & RANKING (M01A) ====================

def process_ingestion_task(job_id: int, sources: List[str], limit_per_source: int):
    """
    Background task to process news ingestion.

    Args:
        job_id: ID of the job record to update
        sources: List of news sources to ingest from
        limit_per_source: Max articles per source
    """
    from app import service_news_ingest
    from app.models import IngestionJob
    import logging

    logger = logging.getLogger(__name__)

    try:
        with Session(engine) as session:
            # Get the existing job
            job_record = session.get(IngestionJob, job_id)
            if not job_record:
                logger.error(f"[BACKGROUND] Job {job_id} not found")
                return

            logger.info(f"[BACKGROUND] Starting ingestion: job_id={job_id}, sources={sources}, limit={limit_per_source}")

            service = service_news_ingest.NewsIngestService(session)
            job, article_ids = service.run_ingestion(
                sources=sources,
                limit_per_source=limit_per_source
            )

            # Update the job record with results
            job_record.status = job.status
            job_record.articles_fetched = job.articles_fetched
            job_record.article_ids = article_ids
            job_record.completed_at = datetime.utcnow()
            session.add(job_record)
            session.commit()

            logger.info(f"[BACKGROUND] Ingestion complete: job_id={job_id}, status={job.status}, articles={job.articles_fetched}, ids={len(article_ids)}")

    except Exception as e:
        logger.error(f"[BACKGROUND] Ingestion error for job {job_id}: {e}", exc_info=True)
        # Mark job as failed
        try:
            with Session(engine) as session:
                job_record = session.get(IngestionJob, job_id)
                if job_record:
                    job_record.status = "failed"
                    job_record.errors = {"error": str(e)}
                    job_record.completed_at = datetime.utcnow()
                    session.add(job_record)
                    session.commit()
        except Exception as update_error:
            logger.error(f"[BACKGROUND] Failed to update job {job_id} error status: {update_error}")


@router.post("/api/news/ingest", status_code=202)
async def ingest_news(
    background_tasks: BackgroundTasks,
    request: schemas_news.IngestRequest = Body(...)
) -> Dict[str, Any]:
    """
    Trigger news ingestion from specified sources (returns immediately, processes in background).

    Args:
        request: Ingestion configuration (sources, limits)
        background_tasks: FastAPI background tasks

    Returns:
        Acknowledgment that ingestion has been queued
    """
    import logging

    logger = logging.getLogger(__name__)

    try:
        logger.info(f"[API] Queuing ingestion: sources={request.sources}, limit={request.limit_per_source}")

        # Create job record immediately before queuing
        from app.models import IngestionJob
        with Session(engine) as session:
            job = IngestionJob(status="running")
            session.add(job)
            session.commit()
            session.refresh(job)
            job_id = job.id

        # Add task to background
        background_tasks.add_task(
            process_ingestion_task,
            job_id,
            request.sources,
            request.limit_per_source
        )

        return {
            "status": "accepted",
            "job_id": job_id,
            "message": f"Ingestion queued for sources: {', '.join(request.sources)}",
            "sources": request.sources,
            "limit_per_source": request.limit_per_source
        }

    except Exception as e:
        logger.error(f"[API] Error queuing ingestion: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to queue ingestion: {str(e)}")


@router.get("/api/news/jobs/{job_id}")
async def get_job_status(
    job_id: int,
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Get status of an ingestion job.

    Args:
        job_id: Job ID to check
        session: Database session

    Returns:
        Job status with article_ids when completed
    """
    from app.models import IngestionJob

    job = session.get(IngestionJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return {
        "job_id": job.id,
        "status": job.status,
        "articles_fetched": job.articles_fetched,
        "article_ids": job.article_ids or [],
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "errors": job.errors
    }


@router.post("/api/news/rank")
async def rank_articles(
    request: "schemas_news.RankRequest",
    session: Session = Depends(get_session)
) -> "schemas_news.RankResponse":
    """
    Rank articles by viral potential using AI.

    Args:
        request: List of article IDs to rank and options
        session: Database session

    Returns:
        Ranking results with scores
    """
    from app import service_news_ranking, schemas_news
    import logging

    logger = logging.getLogger(__name__)

    try:
        logger.info(f"[API] Starting ranking: article_ids={len(request.article_ids)}, force_rerank={request.force_rerank}")

        service = service_news_ranking.NewsRankingService(session)
        results, errors = service.rank_articles(
            article_ids=request.article_ids,
            force_rerank=request.force_rerank
        )

        scores = []
        for article_id, score in results.items():
            scores.append(schemas_news.RankingScoreResponse(
                id=score.id,
                article_id=score.article_id,
                score=score.score,
                reasoning=score.reasoning,
                category=score.category,
                model_used=score.model_used,
                ranked_at=score.ranked_at
            ))

        ranked_count = len([s for s in scores if s.article_id in request.article_ids])
        skipped_count = len(request.article_ids) - ranked_count

        logger.info(f"[API] Ranking complete: ranked={ranked_count}, skipped={skipped_count}, errors={len(errors)}")

        return schemas_news.RankResponse(
            ranked_count=ranked_count,
            skipped_count=skipped_count,
            scores=scores,
            errors=errors if errors else None
        )

    except Exception as e:
        logger.error(f"[API] Ranking error: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ranking failed: {str(e)}")


@router.get("/api/news/articles/pending")
async def get_pending_articles(
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session)
) -> List["schemas_news.ArticleResponse"]:
    """
    Get articles that haven't been ranked yet.

    Args:
        limit: Max number of articles to return
        session: Database session

    Returns:
        List of pending articles
    """
    from app import service_news_ingest, schemas_news

    try:
        service = service_news_ingest.NewsIngestService(session)
        articles = service.get_pending_articles(limit=limit)

        return [
            schemas_news.ArticleResponse(
                id=a.id,
                source_name=a.source_name,
                external_id=a.external_id,
                title=a.title,
                description=a.description,
                content=a.content,
                url=a.url,
                image_url=a.image_url,
                published_at=a.published_at,
                status=a.status,
                fetched_at=a.fetched_at
            )
            for a in articles
        ]

    except Exception as e:
        print(f"[API] Get pending articles error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get articles: {str(e)}")


@router.get("/api/news/articles/top-ranked")
async def get_top_ranked_articles(
    limit: int = Query(default=10, ge=1, le=50),
    min_score: float = Query(default=0.6, ge=0.0, le=1.0),
    session: Session = Depends(get_session)
) -> List["schemas_news.ArticleWithScore"]:
    """
    Get top-ranked articles ready for script generation.

    Args:
        limit: Max number of articles to return
        min_score: Minimum viral potential score (0-1)
        session: Database session

    Returns:
        List of articles with their ranking scores
    """
    from app import service_news_ranking, schemas_news

    try:
        service = service_news_ranking.NewsRankingService(session)
        results = service.get_top_ranked_articles(limit=limit, min_score=min_score)

        return [
            schemas_news.ArticleWithScore(
                article=schemas_news.ArticleResponse(
                    id=article.id,
                    source_name=article.source_name,
                    external_id=article.external_id,
                    title=article.title,
                    description=article.description,
                    content=article.content,
                    url=article.url,
                    image_url=article.image_url,
                    published_at=article.published_at,
                    status=article.status,
                    fetched_at=article.fetched_at
                ),
                score=schemas_news.RankingScoreResponse(
                    id=score.id,
                    article_id=score.article_id,
                    score=score.score,
                    reasoning=score.reasoning,
                    category=score.category,
                    model_used=score.model_used,
                    ranked_at=score.ranked_at
                )
            )
            for article, score in results
        ]

    except Exception as e:
        print(f"[API] Get top ranked articles error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get articles: {str(e)}")


@router.get("/api/news/articles/{article_id}")
async def get_article_with_score(
    article_id: int,
    session: Session = Depends(get_session)
) -> "schemas_news.ArticleWithScore":
    """
    Get a single article with its latest ranking score.

    Args:
        article_id: Article ID
        session: Database session

    Returns:
        Article with ranking score (if available)
    """
    from app import service_news_ingest, service_news_ranking, schemas_news

    try:
        ingest_service = service_news_ingest.NewsIngestService(session)
        ranking_service = service_news_ranking.NewsRankingService(session)

        article = ingest_service.get_article_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail=f"Article {article_id} not found")

        score = ranking_service.get_latest_score_for_article(article_id)

        article_response = schemas_news.ArticleResponse(
            id=article.id,
            source_name=article.source_name,
            external_id=article.external_id,
            title=article.title,
            description=article.description,
            content=article.content,
            url=article.url,
            image_url=article.image_url,
            published_at=article.published_at,
            status=article.status,
            fetched_at=article.fetched_at
        )

        score_response = None
        if score:
            score_response = schemas_news.RankingScoreResponse(
                id=score.id,
                article_id=score.article_id,
                score=score.score,
                reasoning=score.reasoning,
                category=score.category,
                model_used=score.model_used,
                ranked_at=score.ranked_at
            )

        return schemas_news.ArticleWithScore(
            article=article_response,
            score=score_response
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Get article error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get article: {str(e)}")


# ==================== END NEWS INGESTION & RANKING ====================
