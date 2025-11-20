# 🎬 Xseller.ai - AI-Powered Social Media Video Automation

**Gemini-powered MVP** for automatically generating viral short-form videos from news sources.

## 🚀 Overview

Xseller.ai transforms news articles into engaging 15-30 second social media videos optimized for TikTok, Instagram Reels, and YouTube Shorts. The system handles content discovery, script generation, voiceover synthesis, video assembly, and publishing—fully autonomously.

## 🏗️ Architecture

**AI/LLM Stack:**
- **Primary LLM:** Google Gemini 2.0 Flash (via API)
- **Heavy Workloads:** Gemini 1.5 Pro (via GitHub Actions offload)
- **Script Generation:** OpenAI GPT-4o-mini
- **Voice Generation:** ElevenLabs + OpenAI TTS + gTTS (fallback)

**Infrastructure:**
- **Backend:** FastAPI (Python 3.11+)
- **Database:** SQLite (dev), PostgreSQL (production)
- **Deployment:** Railway (automatic from main branch)
- **Scheduling:** GitHub Actions cron workflows
- **CI/CD:** GitHub Actions (linting, testing, guardrails)

## 📦 Key Components

- **M01 Content Pipeline:** News ingestion + AI ranking (✅ Complete)
- **M02-M05:** Media production, video assembly, review, publishing (🚧 In Progress)
- **LLM Router:** Intelligent workload distribution (Gemini Flash ↔ Gemini Pro)
- **CI Monitoring:** Autonomous GitHub Actions tracking

## 🔑 Required API Keys

```bash
GEMINI_API_KEY=       # Google Gemini (primary LLM)
OPENAI_API_KEY=       # GPT-4o-mini (scripts)
NEWS_API_KEY=         # NewsAPI.org
ELEVENLABS_API_KEY=   # Voice synthesis
PEXELS_API_KEY=       # Stock footage
DATABASE_URL=         # PostgreSQL/SQLite
```

## 🚦 Quick Start

```bash
# Setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your API keys

# Run
uvicorn app.main:app --reload
# API: http://localhost:8000/docs

# Test
pytest --cov=app

# Monitor CI
./monitor_ci.sh
```

## 📅 Automated Schedule

- **M01 Daily Batch:** 9:00am NZDT (news ingestion + ranking + scripts)
- **M02 Media Production:** 9:30am NZDT (voice + B-roll search)
- **M03 Video Assembly:** 10:00am NZDT (assembly + overlays + QC)
- **M04 Review:** 10:30am NZDT (review queue preparation)
- **M05 Publishing:** 11:00am NZDT (publish + analytics + learning)
- **Backend CI:** On every push
- **Guardrails Check:** On PRs

## 📚 Documentation

- Architecture: `.claude/ARCHITECTURE.md`
- CI Monitoring: `.github/README_CI_MONITOR.md`
- API Docs: `/docs` (Swagger UI)
- Frontend API: See **API Endpoints** section below

---

## 🌐 API Endpoints

**Base URL:** `https://strong-encouragement-xsellerai.up.railway.app`

### Health & Stats

#### `GET /api/health`
Check backend health status.

**Response:**
```json
{
  "api": "healthy",
  "database": "connected",
  "scheduler": "running"
}
```

#### `GET /api/stats/dashboard`
Get dashboard statistics for the frontend.

**Response:**
```json
{
  "queue_stats": {
    "draft": 0,
    "approved": 0,
    "published_today": 0,
    "overdue": 0,
    "failed": 0
  },
  "recent_activity": []
}
```

### Content Management

#### `GET /api/content/queue`
Get all posts in the review queue.

**Query Parameters:**
- `status` (optional): Filter by status (`draft`, `approved`, `rejected`, `published`)
- `limit` (optional): Max number of posts to return
- `offset` (optional): Pagination offset

**Response:**
```json
{
  "posts": [
    {
      "id": 1,
      "title": "Breaking News: ...",
      "script": "...",
      "status": "draft",
      "created_at": "2025-11-20T10:00:00Z",
      "video_url": null
    }
  ],
  "total": 1
}
```

#### `POST /api/content/{post_id}/approve`
Approve a post for publishing.

**Response:**
```json
{
  "id": 1,
  "status": "approved",
  "message": "Post approved"
}
```

#### `POST /api/content/{post_id}/reject`
Reject a post.

**Request Body:**
```json
{
  "reason": "Not engaging enough"
}
```

**Response:**
```json
{
  "id": 1,
  "status": "rejected",
  "message": "Post rejected"
}
```

#### `PATCH /api/content/{post_id}`
Update post content (title, script, etc.).

**Request Body:**
```json
{
  "title": "Updated title",
  "script": "Updated script"
}
```

#### `DELETE /api/content/{post_id}`
Delete a post.

### News & Articles

#### `GET /api/news/articles/pending`
Get pending news articles (not yet processed).

**Response:**
```json
[
  {
    "id": 1,
    "title": "Article title",
    "description": "...",
    "url": "https://...",
    "published_at": "2025-11-20T08:00:00Z",
    "source_name": "newsapi"
  }
]
```

#### `GET /api/news/articles/top-ranked`
Get top-ranked articles.

**Query Parameters:**
- `min_score` (optional): Minimum ranking score (0.0-1.0)
- `limit` (optional): Max number of articles

**Response:**
```json
[
  {
    "id": 1,
    "title": "Top article",
    "ranking_score": 0.92,
    "viral_score": 0.88,
    "approved_for_script": true
  }
]
```

#### `POST /api/news/ingest`
Trigger manual news ingestion.

**Request Body:**
```json
{
  "sources": ["newsapi", "mock"],
  "limit_per_source": 20
}
```

**Response:**
```json
{
  "status": "accepted",
  "job_id": 1,
  "message": "Ingestion queued for sources: newsapi, mock"
}
```

#### `GET /api/news/jobs/{job_id}`
Get status of an ingestion/ranking job.

**Response:**
```json
{
  "job_id": 1,
  "status": "completed",
  "articles_fetched": 15,
  "article_ids": [1, 2, 3, ...],
  "started_at": "2025-11-20T09:00:00Z",
  "completed_at": "2025-11-20T09:00:05Z",
  "errors": null
}
```

#### `POST /api/news/rank`
Trigger manual ranking of articles.

**Request Body:**
```json
{
  "article_ids": [1, 2, 3],
  "min_score": 0.6,
  "force_rerank": false
}
```

### Video Generation

#### `POST /api/content/{post_id}/generate-video`
Generate video for an approved post.

#### `GET /api/content/{post_id}/video-status`
Check video generation status.

#### `POST /api/content/{post_id}/regenerate-video`
Regenerate video with different parameters.

### Voice

#### `GET /api/voice/available`
Get list of available voices.

#### `POST /api/voice/preview/{post_id}`
Generate voice preview for a post.

#### `POST /api/voice/select/{post_id}`
Select voice for a post.

**Request Body:**
```json
{
  "voice_id": "eleven_monolingual_v1",
  "energy_mode": "high"
}
```

---

## 🔒 CORS Configuration

**Allowed Origins:**
- `http://localhost:3000` (development)
- Can be configured via `ALLOWED_ORIGINS` environment variable

**Example:**
```bash
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app
```

**Headers:**
- All methods allowed (`GET`, `POST`, `PATCH`, `DELETE`, etc.)
- All headers allowed
- Credentials supported

---

## 🧪 Testing API Endpoints

```bash
# Health check
curl https://strong-encouragement-xsellerai.up.railway.app/api/health

# Dashboard stats
curl https://strong-encouragement-xsellerai.up.railway.app/api/stats/dashboard

# Content queue
curl https://strong-encouragement-xsellerai.up.railway.app/api/content/queue

# Pending articles
curl https://strong-encouragement-xsellerai.up.railway.app/api/news/articles/pending

# Trigger ingestion
curl -X POST https://strong-encouragement-xsellerai.up.railway.app/api/news/ingest \
  -H "Content-Type: application/json" \
  -d '{"sources": ["mock"], "limit_per_source": 5}'
```

---

**Status:** 🟢 Production | **Version:** MVP 1.0 | **Updated:** Nov 20, 2025
