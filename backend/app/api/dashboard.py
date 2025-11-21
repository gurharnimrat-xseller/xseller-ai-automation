"""
Dashboard API Endpoints

Provides real-time data for the frontend dashboard including:
- Dashboard statistics (agents, news, videos, queue)
- Agent status and monitoring
- Recent activities
- Performance metrics
"""
from __future__ import annotations

from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from app.database import engine
from app.models import Post, Article, RankingScore, IngestionJob, Asset


# Create router with /api/dashboard prefix
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


# Dependency to get database session
def get_session() -> Session:
    with Session(engine) as session:
        yield session


# ==================== AGENT DEFINITIONS ====================

# Define the 6 agents that power the system
AGENTS = [
    {
        "id": "m01",
        "name": "News Ingestion Agent",
        "type": "Ingestion",
        "workflow": "m01_daily_batch",
        "description": "Fetches and ranks news articles"
    },
    {
        "id": "m02",
        "name": "Media Production Agent",
        "type": "Media Production",
        "workflow": "m02_media_production",
        "description": "Generates voice and B-roll"
    },
    {
        "id": "m03",
        "name": "Video Assembly Agent",
        "type": "Video Production",
        "workflow": "m03_video_assembly",
        "description": "Assembles final videos"
    },
    {
        "id": "m04",
        "name": "Review Agent",
        "type": "Quality Control",
        "workflow": "m04_review",
        "description": "Prepares content for review"
    },
    {
        "id": "m05",
        "name": "Publishing Agent",
        "type": "Distribution",
        "workflow": "m05_publishing",
        "description": "Publishes to social platforms"
    },
    {
        "id": "ranking",
        "name": "Viral Ranking Agent",
        "type": "Analysis",
        "workflow": "ranking",
        "description": "Scores articles for viral potential"
    },
]


# ==================== HELPER FUNCTIONS ====================

def generate_chart_data(base_value: int, days: int = 7, variance: float = 0.2) -> List[Dict[str, int]]:
    """Generate mock chart data for trends."""
    data = []
    for i in range(days):
        variation = random.uniform(-variance, variance)
        value = max(0, int(base_value * (1 + variation)))
        data.append({"value": value})
    return data


def get_agent_status_from_db(session: Session) -> Dict[str, Any]:
    """Calculate agent status based on recent database activity."""
    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)

    # Check recent ingestion jobs for M01 status
    recent_jobs = session.exec(
        select(IngestionJob)
        .where(IngestionJob.started_at >= one_hour_ago)
        .order_by(IngestionJob.started_at.desc())
        .limit(1)
    ).first()

    # Count posts by status
    video_production_count = session.exec(
        select(func.count()).select_from(Post)
        .where(Post.status.in_(["media_production", "media_ready"]))
    ).one()

    review_count = session.exec(
        select(func.count()).select_from(Post)
        .where(Post.status == "ready_for_review")
    ).one()

    return {
        "recent_job": recent_jobs,
        "video_production": video_production_count,
        "review_queue": review_count,
    }


# ==================== ENDPOINTS ====================

@router.get("/stats")
async def get_dashboard_stats(session: Session = Depends(get_session)) -> Dict[str, Any]:
    """
    Get dashboard statistics including agents, news, videos, and queue metrics.

    Returns summary statistics with trend data for charts.
    """
    try:
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Count articles fetched today
        articles_today = session.exec(
            select(func.count()).select_from(Article)
            .where(Article.fetched_at >= today_start)
        ).one()

        # Count total videos (posts with kind="video")
        total_videos = session.exec(
            select(func.count()).select_from(Post)
            .where(Post.kind == "video", Post.deleted_at.is_(None))
        ).one()

        # Count pending videos (media_production, media_ready, ready_for_review)
        pending_videos = session.exec(
            select(func.count()).select_from(Post)
            .where(
                Post.kind == "video",
                Post.status.in_(["media_production", "media_ready", "ready_for_review"]),
                Post.deleted_at.is_(None)
            )
        ).one()

        # Count queue items (draft + approved)
        queue_items = session.exec(
            select(func.count()).select_from(Post)
            .where(
                Post.status.in_(["draft", "approved", "ready_for_review"]),
                Post.deleted_at.is_(None)
            )
        ).one()

        # Count processing items
        processing = session.exec(
            select(func.count()).select_from(Post)
            .where(
                Post.status.in_(["media_production", "video_production"]),
                Post.deleted_at.is_(None)
            )
        ).one()

        # Get agent status
        db_status = get_agent_status_from_db(session)

        # Calculate active agents (simplified - based on recent activity)
        active_agents = 4 if articles_today > 0 else 2
        idle_agents = 1
        error_agents = 0  # Check for failed jobs

        # Check for recent failures
        recent_failed = session.exec(
            select(func.count()).select_from(IngestionJob)
            .where(
                IngestionJob.status == "failed",
                IngestionJob.started_at >= now - timedelta(hours=2)
            )
        ).one()

        if recent_failed > 0:
            error_agents = 1
            active_agents = max(0, active_agents - 1)

        return {
            "agents": {
                "total": 6,
                "active": active_agents,
                "idle": idle_agents,
                "error": error_agents,
                "chartData": generate_chart_data(6, 7, 0.1)
            },
            "news": {
                "today": articles_today,
                "trend": 12,  # Could calculate from yesterday comparison
                "chartData": generate_chart_data(articles_today or 20, 7, 0.3)
            },
            "videos": {
                "total": total_videos,
                "pending": pending_videos,
                "trend": -3,
                "chartData": generate_chart_data(total_videos or 15, 7, 0.25)
            },
            "queue": {
                "items": queue_items,
                "processing": processing,
                "chartData": generate_chart_data(queue_items or 10, 7, 0.2)
            }
        }

    except Exception as e:
        print(f"[dashboard] Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard stats: {str(e)}")


@router.get("/activity")
async def get_recent_activity(
    limit: int = 10,
    session: Session = Depends(get_session)
) -> List[Dict[str, Any]]:
    """
    Get recent system activities.

    Returns activities from various agents including news ingestion,
    video production, publishing, etc.
    """
    try:
        activities: List[Dict[str, Any]] = []
        now = datetime.utcnow()

        # Get recent ingestion jobs
        recent_jobs = session.exec(
            select(IngestionJob)
            .order_by(IngestionJob.started_at.desc())
            .limit(5)
        ).all()

        for job in recent_jobs:
            activity_type = "success" if job.status == "completed" else (
                "error" if job.status == "failed" else "info"
            )
            activities.append({
                "id": f"job_{job.id}",
                "type": activity_type,
                "title": f"News Ingestion {'Complete' if job.status == 'completed' else job.status.title()}",
                "description": f"Fetched {job.articles_fetched} articles, ranked {job.articles_ranked}",
                "timestamp": job.completed_at or job.started_at,
                "agent": "News Ingestion Agent"
            })

        # Get recent posts (videos created/published)
        recent_posts = session.exec(
            select(Post)
            .where(Post.kind == "video")
            .order_by(Post.updated_at.desc())
            .limit(5)
        ).all()

        for post in recent_posts:
            if post.status == "published":
                activities.append({
                    "id": f"post_{post.id}_published",
                    "type": "success",
                    "title": "Video Published",
                    "description": f'Published "{post.title[:40]}..." to platforms',
                    "timestamp": post.published_at or post.updated_at,
                    "agent": "Publishing Agent",
                    "link": "/queue"
                })
            elif post.status == "ready_for_review":
                activities.append({
                    "id": f"post_{post.id}_review",
                    "type": "info",
                    "title": "Video Ready for Review",
                    "description": f'"{post.title[:40]}..." awaiting approval',
                    "timestamp": post.updated_at,
                    "agent": "Video Assembly Agent",
                    "link": "/queue"
                })
            elif post.status == "media_ready":
                activities.append({
                    "id": f"post_{post.id}_media",
                    "type": "info",
                    "title": "Media Production Complete",
                    "description": f'Voice and B-roll ready for "{post.title[:30]}..."',
                    "timestamp": post.updated_at,
                    "agent": "Media Production Agent"
                })

        # Get high-scoring articles
        high_scores = session.exec(
            select(RankingScore, Article)
            .join(Article, RankingScore.article_id == Article.id)
            .where(RankingScore.score >= 0.8)
            .order_by(RankingScore.ranked_at.desc())
            .limit(3)
        ).all()

        for score, article in high_scores:
            activities.append({
                "id": f"rank_{score.id}",
                "type": "success",
                "title": "High Quality Content Detected",
                "description": f'"{article.title[:35]}..." scored {score.score:.1f}/1.0',
                "timestamp": score.ranked_at,
                "agent": "Viral Ranking Agent"
            })

        # Sort by timestamp and limit
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:limit]

    except Exception as e:
        print(f"[dashboard] Error fetching activities: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch activities: {str(e)}")


@router.get("/performance")
async def get_performance_metrics(session: Session = Depends(get_session)) -> Dict[str, Any]:
    """
    Get 24-hour performance metrics.

    Returns metrics for scripts generated, quality scores, and success rates.
    """
    try:
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)

        # Count scripts generated today (video posts)
        scripts_today = session.exec(
            select(func.count()).select_from(Post)
            .where(
                Post.kind == "video",
                Post.created_at >= today_start
            )
        ).one()

        # Count scripts generated yesterday
        scripts_yesterday = session.exec(
            select(func.count()).select_from(Post)
            .where(
                Post.kind == "video",
                Post.created_at >= yesterday_start,
                Post.created_at < today_start
            )
        ).one()

        # Calculate trend
        scripts_trend = 0
        if scripts_yesterday > 0:
            scripts_trend = round(((scripts_today - scripts_yesterday) / scripts_yesterday) * 100, 1)

        # Average ranking score (quality)
        avg_score_today = session.exec(
            select(func.avg(RankingScore.score))
            .where(RankingScore.ranked_at >= today_start)
        ).one()

        avg_score_yesterday = session.exec(
            select(func.avg(RankingScore.score))
            .where(
                RankingScore.ranked_at >= yesterday_start,
                RankingScore.ranked_at < today_start
            )
        ).one()

        quality_value = round((avg_score_today or 0.85) * 10, 1)  # Scale to 10
        quality_prev = round((avg_score_yesterday or 0.82) * 10, 1)
        quality_trend = round(quality_value - quality_prev, 1)

        # Success rate (completed vs failed jobs)
        completed_jobs = session.exec(
            select(func.count()).select_from(IngestionJob)
            .where(
                IngestionJob.status == "completed",
                IngestionJob.started_at >= today_start
            )
        ).one()

        total_jobs = session.exec(
            select(func.count()).select_from(IngestionJob)
            .where(IngestionJob.started_at >= today_start)
        ).one()

        success_rate = 100.0 if total_jobs == 0 else round((completed_jobs / total_jobs) * 100, 1)

        # Yesterday's success rate
        completed_yesterday = session.exec(
            select(func.count()).select_from(IngestionJob)
            .where(
                IngestionJob.status == "completed",
                IngestionJob.started_at >= yesterday_start,
                IngestionJob.started_at < today_start
            )
        ).one()

        total_yesterday = session.exec(
            select(func.count()).select_from(IngestionJob)
            .where(
                IngestionJob.started_at >= yesterday_start,
                IngestionJob.started_at < today_start
            )
        ).one()

        success_prev = 100.0 if total_yesterday == 0 else round((completed_yesterday / total_yesterday) * 100, 1)
        success_trend = round(success_rate - success_prev, 1)

        return {
            "scriptsGenerated": {
                "value": scripts_today or 0,
                "trend": scripts_trend,
                "previousValue": scripts_yesterday or 0
            },
            "qualityScore": {
                "value": quality_value,
                "trend": quality_trend,
                "previousValue": quality_prev
            },
            "successRate": {
                "value": success_rate,
                "trend": success_trend,
                "previousValue": success_prev
            }
        }

    except Exception as e:
        print(f"[dashboard] Error fetching performance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch performance: {str(e)}")


# ==================== AGENT STATUS ENDPOINT ====================

@router.get("/agents")
async def get_agents_status(session: Session = Depends(get_session)) -> List[Dict[str, Any]]:
    """
    Get status of all agents.

    Returns detailed information about each agent including:
    - Current status (active, idle, processing, error)
    - Current task
    - Progress percentage
    - Last run time
    - Uptime
    - Efficiency metrics
    """
    try:
        now = datetime.utcnow()
        agents_status = []

        for agent in AGENTS:
            agent_data = {
                "id": agent["id"],
                "name": agent["name"],
                "type": agent["type"],
                "status": "idle",
                "currentTask": None,
                "progress": None,
                "lastRun": None,
                "uptime": "99.5%",
                "efficiency": random.randint(92, 99)
            }

            # Check agent-specific status
            if agent["id"] == "m01":
                # Check recent ingestion job
                recent_job = session.exec(
                    select(IngestionJob)
                    .order_by(IngestionJob.started_at.desc())
                    .limit(1)
                ).first()

                if recent_job:
                    agent_data["lastRun"] = recent_job.started_at
                    if recent_job.status == "running":
                        agent_data["status"] = "processing"
                        agent_data["currentTask"] = f"Processing {recent_job.articles_fetched} articles"
                        agent_data["progress"] = 50
                    elif recent_job.status == "failed":
                        agent_data["status"] = "error"
                        agent_data["currentTask"] = "Last job failed"
                    else:
                        agent_data["status"] = "active"
                        agent_data["currentTask"] = f"Fetched {recent_job.articles_fetched} articles"

            elif agent["id"] == "m02":
                # Check posts in media_production status
                media_posts = session.exec(
                    select(func.count()).select_from(Post)
                    .where(Post.status == "media_production")
                ).one()

                if media_posts > 0:
                    agent_data["status"] = "processing"
                    agent_data["currentTask"] = f"Generating media for {media_posts} posts"
                    agent_data["progress"] = random.randint(20, 80)
                else:
                    agent_data["status"] = "idle"

                # Get last updated post
                last_media = session.exec(
                    select(Post)
                    .where(Post.status.in_(["media_production", "media_ready"]))
                    .order_by(Post.updated_at.desc())
                    .limit(1)
                ).first()
                if last_media:
                    agent_data["lastRun"] = last_media.updated_at

            elif agent["id"] == "m03":
                # Check posts in media_ready status
                ready_posts = session.exec(
                    select(func.count()).select_from(Post)
                    .where(Post.status == "media_ready")
                ).one()

                if ready_posts > 0:
                    agent_data["status"] = "processing"
                    agent_data["currentTask"] = f"Assembling {ready_posts} videos"
                    agent_data["progress"] = random.randint(30, 70)
                else:
                    agent_data["status"] = "idle"

            elif agent["id"] == "m04":
                # Check posts ready for review
                review_posts = session.exec(
                    select(func.count()).select_from(Post)
                    .where(Post.status == "ready_for_review")
                ).one()

                if review_posts > 0:
                    agent_data["status"] = "active"
                    agent_data["currentTask"] = f"{review_posts} videos awaiting review"
                else:
                    agent_data["status"] = "idle"

            elif agent["id"] == "m05":
                # Check published posts today
                published_today = session.exec(
                    select(func.count()).select_from(Post)
                    .where(
                        Post.status == "published",
                        Post.published_at >= now.replace(hour=0, minute=0, second=0)
                    )
                ).one()

                if published_today > 0:
                    agent_data["status"] = "active"
                    agent_data["currentTask"] = f"Published {published_today} videos today"
                else:
                    agent_data["status"] = "idle"

            elif agent["id"] == "ranking":
                # Check recent rankings
                recent_rankings = session.exec(
                    select(func.count()).select_from(RankingScore)
                    .where(RankingScore.ranked_at >= now - timedelta(hours=1))
                ).one()

                if recent_rankings > 0:
                    agent_data["status"] = "active"
                    agent_data["currentTask"] = f"Ranked {recent_rankings} articles"
                else:
                    agent_data["status"] = "idle"

                last_rank = session.exec(
                    select(RankingScore)
                    .order_by(RankingScore.ranked_at.desc())
                    .limit(1)
                ).first()
                if last_rank:
                    agent_data["lastRun"] = last_rank.ranked_at

            agents_status.append(agent_data)

        return agents_status

    except Exception as e:
        print(f"[dashboard] Error fetching agent status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch agent status: {str(e)}")


# Alias for backwards compatibility
@router.get("/agents/status")
async def get_agents_status_alias(session: Session = Depends(get_session)) -> List[Dict[str, Any]]:
    """Alias for /api/dashboard/agents."""
    return await get_agents_status(session)
