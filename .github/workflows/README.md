# GitHub Actions Workflows - Overview

This document describes all active GitHub Actions workflows in this repository and their purposes.

## Core Workflows

### 1. CI (Main CI/CD Pipeline) - `ci.yml`
**Triggers:** Push to `main`, Pull Requests, Manual dispatch  
**Purpose:** Main continuous integration pipeline  

**Jobs:**
- **Guardrails / scan** - Verifies no direct AI SDK imports (uses router pattern)
- **Lint (Python)** - Runs `ruff` and `mypy` on Python code
- **Lint (Node)** - Runs ESLint on Node.js/TypeScript code  
- **Tests (Python)** - Runs pytest suite
- **Tests (Node)** - Runs Node test suite

**Key Features:**
- Least-privilege permissions (contents: read only)
- Concurrency control (cancels in-progress runs on same branch)
- Dependency caching for faster runs
- All jobs depend on guardrails passing first

---

### 2. M01 Daily Batch (News Ingestion + Ranking) - `m01_daily_batch.yml`
**Triggers:** 
- **Schedule:** Daily at 20:00 UTC 
  - **NZT Time:** ~09:00 during Nov-Mar (standard time), ~08:00 during Apr-Oct (DST)
- **Manual:** Can be triggered from GitHub UI via "Run workflow"

**Purpose:** Automated daily news ingestion and ranking pipeline

**What it does when it runs:**
1. **Fetches** news articles from configured sources (NewsAPI, Mock)
2. **Ingests** up to 20 articles per source via backend API
3. **Ranks** articles using AI scoring (minimum score: 0.6)
4. **Stores** results in database for later retrieval by frontend

**Configuration Required (GitHub Secrets):**
- `BACKEND_API_BASE_URL` - Your backend API endpoint (e.g., `https://api.xseller.ai`)

**Runtime:** 
- Approximately 5-10 minutes depending on article count and API response times
- Includes dependency caching for faster subsequent runs

**Next Scheduled Run:** Every day at ~09:00 NZT (20:00 UTC)

**Script Location:** `backend/app/jobs/m01_daily_batch.py`

---

### 3. Backend CI - `backend-ci.yml`
**Triggers:** Push to specific backend paths  
**Purpose:** Backend-specific CI checks (may be redundant with main CI)

---

### 4. Frontend CI - `frontend-ci.yml`
**Triggers:** Push to specific frontend paths  
**Purpose:** Frontend-specific CI checks (may be redundant with main CI)

---

## Monitoring & Automation Workflows

### 5. Monitor - `monitor.yml`
**Triggers:** Scheduled daily  
**Purpose:** Daily monitoring and health checks

---

## Code Review & Development Workflows

### 6. Claude Code Review - `claude-code-review.yml`
**Triggers:** Pull Request events  
**Purpose:** Automated code review using Claude AI

---

### 7. Claude Code - `claude.yml`
**Triggers:** Workflow dispatch (manual)  
**Purpose:** Claude-assisted code generation and refactoring

---

### 8. Bootstrap Architect - `bootstrap_architect.yml`
**Triggers:** Workflow dispatch (manual)  
**Purpose:** Project setup and architecture scaffolding

---

### 9. Offload Gemini - `offload_gemini.yml`
**Triggers:** Workflow dispatch (manual)  
**Purpose:** Offload heavy AI tasks to Gemini API

---

## Recent Changes (This PR)

### ✅ Removed
- **`guardrails.yml`** - Redundant workflow that duplicated the guardrails job in `ci.yml`
  - Same checks were running twice on every PR
  - `ci.yml` version has better security (explicit permissions) and concurrency control
  - **Impact:** Cleaner workflow runs, no functional changes

### ✅ Enhanced
- **`m01_daily_batch.yml`** - Improvements:
  - ✨ **Clearer timezone documentation** - Explains NZT ↔ UTC conversion for schedule
  - 🔒 **Concurrency control** - Prevents overlapping batch runs
  - ⚡ **Dependency caching** - Faster runs via pip cache
  - 📝 **Better inline comments** - Explains what each step does

---

## Best Practices Applied

All workflows follow these principles from `docs/style/actions_least_privilege.md`:

1. **Least Privilege** - Only grant permissions each job actually needs
2. **No Secrets in Code** - Use `${{ secrets.* }}` and `${{ vars.* }}` only
3. **Concurrency Control** - Prevent overlapping runs where appropriate
4. **Caching** - Cache dependencies (pip, npm) for faster runs
5. **Idempotence** - Re-runs produce same results

---

## Setup Instructions

### For M01 Daily Batch to Run Successfully

Configure this secret in **GitHub Settings → Secrets and variables → Actions**:

- **`BACKEND_API_BASE_URL`** - Your backend API URL (e.g., `https://api.xseller.ai`)
  - Must be publicly accessible from GitHub Actions runners
  - Should have `/api/news/ingest` and `/api/news/rank` endpoints available

### Testing M01 Manually

1. Go to **Actions** tab in GitHub
2. Select **"M01 Daily Batch"** workflow
3. Click **"Run workflow"** button
4. Select branch (usually `main`)
5. Click green **"Run workflow"** button
6. Monitor the run in the Actions tab

---

## Troubleshooting

### M01 Daily Batch Not Running?
1. ✅ Check that `BACKEND_API_BASE_URL` secret is configured
2. ✅ Verify backend API is accessible from GitHub Actions runners
3. ✅ Check workflow run logs for specific errors (Actions tab → M01 Daily Batch)
4. ✅ Test manually using "Run workflow" button

### CI Failing?
1. ✅ Check if it's a guardrails violation (direct AI SDK imports without router)
2. ✅ Look for lint errors (ruff, mypy, eslint)
3. ✅ Check if tests are failing
4. ✅ Only the "Guardrails / scan" job is required for branch protection initially

### Workflow Not Triggering?
1. ✅ Check the `on:` triggers in the workflow file
2. ✅ For scheduled workflows, they only run on the default branch (usually `main`)
3. ✅ For path-filtered workflows, ensure relevant files changed

---

## Local Development

Run checks locally before pushing to catch issues early:

### Backend
```bash
cd backend
python -m pip install --upgrade pip
pip install ruff mypy pytest pytest-cov
pip install -r requirements.txt

# Run checks
python agents/checks/verify_guardrails.py  # Guardrails
ruff check .                                 # Linting
mypy .                                       # Type checking
pytest -q                                    # Tests
```

### Frontend
```bash
cd frontend
npm ci

# Run checks
npm run lint                                 # ESLint
npx tsc --noEmit                            # Type checking
npm run build                                # Build
npm test                                     # Tests (if configured)
```

### M01 Daily Batch (Local Testing)
```bash
cd backend
python -m app.jobs.m01_daily_batch \
  --base-url "http://localhost:8000" \
  --sources "mock" \
  --limit-per-source "5" \
  --min-score "0.6"
```

---

## What Happens After Merging This PR

### Immediately
- ✅ Redundant `guardrails.yml` will stop running (one less workflow to maintain)
- ✅ CI will continue working exactly as before (no changes to `ci.yml`)
- ✅ M01 daily batch workflow becomes active

### Daily Starting Tomorrow
- 🕐 **Every day at ~09:00 NZT (20:00 UTC):**
  1. M01 workflow triggers automatically
  2. Fetches latest news from configured sources
  3. Ingests articles via backend API (`/api/news/ingest`)
  4. Ranks articles using AI (`/api/news/rank` with min_score=0.6)
  5. Completes in 5-10 minutes
  6. Check logs in **Actions** tab to see results

### No Manual Work Required After Merge
- 🎉 Just click "Merge" and the automation takes over
- 📊 Check Actions tab daily to monitor M01 batch runs
- 🔔 Add notifications later if desired (Slack, email, etc.)

---

## Future Improvements

Potential enhancements to consider:

1. 📧 Add Slack/email notifications for M01 batch failures
2. 📊 Add metrics collection (articles fetched, ranked, processing time)
3. 🔄 Add retry logic for transient API failures
4. 📅 Configure different schedules for weekdays vs weekends
5. 🧹 Consolidate backend-ci.yml and frontend-ci.yml into main ci.yml if redundant
