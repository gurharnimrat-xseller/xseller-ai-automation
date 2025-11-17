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

- **M01 Daily Batch:** 9am NZDT (news ingestion)
- **Backend CI:** On every push
- **Guardrails Check:** On PRs

## 📚 Documentation

- Architecture: `.claude/ARCHITECTURE.md`
- CI Monitoring: `.github/README_CI_MONITOR.md`
- API Docs: `/docs` (Swagger UI)

---

**Status:** 🟢 Production | **Version:** MVP 1.0 | **Updated:** Nov 18, 2025
