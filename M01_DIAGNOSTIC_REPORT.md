# 🔥 M01 Daily Batch - Complete System Diagnostic Report

**Generated**: 2025-11-13T22:54 UTC  
**Status**: **NOT READY** ❌

---

## 📋 Executive Summary

M01 Daily Batch workflow **CANNOT** run autonomously tomorrow at 9AM NZT without intervention. Two critical issues must be resolved:

1. ✅ **Python module path** - FIXED in this PR
2. ❌ **Missing BACKEND_API_BASE_URL secret** - Requires manual configuration

---

## 1️⃣ Current Exact State

### Workflow Files

#### `.github/workflows/ci.yml`
- **Status**: ✅ Active
- **Triggers**: push to main, pull_request, workflow_dispatch
- **Guardrails**: Inline check at job level (lines 16-26)
- **Dependencies**: None
- **Conflicts**: None

#### `.github/workflows/m01_daily_batch.yml`
- **Status**: ✅ Active
- **Schedule**: `0 20 * * *` (20:00 UTC / 9AM NZT)
- **Last Run**: Failed at 2025-11-13T20:16:43Z
- **Issues**: 2 blocking issues (see below)

#### `.github/workflows/guardrails.yml`
- **Status**: ✅ Active (PR-only)
- **Triggers**: pull_request only
- **Shadow Running**: NO - does not interfere with other workflows
- **Purpose**: Additional PR validation

#### `.github/workflows/monitor.yml`
- **Status**: ⏸️ Paused
- **Schedule**: `0 0 1 1 *` (once per year)
- **Impact**: None

### Key Files

#### `backend/app/jobs/m01_daily_batch.py`
- **Status**: ✅ Exists and functional
- **Purpose**: Orchestrates M01 news ingestion + ranking
- **Dependencies**: 
  - agents.checks.router (for guardrails compliance)
  - Backend API endpoints (via BACKEND_API_BASE_URL)

#### `backend/app/__init__.py`
- **Status**: ⚠️ Contains import that requires special handling
- **Line 1**: `from agents.checks.router import should_offload, offload_to_gemini`
- **Issue**: Import fails when Python runs from `backend/` directory

---

## 2️⃣ Workflow Dependencies & Conflicts

### Analysis Results

✅ **NO CONFLICTS DETECTED**

- CI workflow includes independent guardrails check
- guardrails.yml only runs on pull_requests
- M01 workflow is independent and isolated
- Monitor workflow is effectively disabled

### Dependency Graph

```
ci.yml
├── Inline guardrails check (independent)
├── lint_python (depends on guardrails)
├── lint_node (depends on guardrails)
├── tests_python (depends on lint_python)
└── tests_node (depends on lint_node)

guardrails.yml (PR-only, no dependencies)

m01_daily_batch.yml (isolated, no dependencies)

monitor.yml (paused)
```

---

## 3️⃣ M01 Workflow Failure Analysis

### Last 3 Runs

Only 1 run exists:
- **Run ID**: 19344616800
- **Date**: 2025-11-13T20:16:43Z
- **Event**: schedule (cron trigger)
- **Conclusion**: ❌ failure

### Detailed Failure Breakdown

#### **Issue #1: ModuleNotFoundError** 🔴

**Timestamp**: `2025-11-13T20:17:08.868Z`

**File Path**: `backend/app/__init__.py`

**Line Number**: 1

**Exact Error Message**:
```
Traceback (most recent call last):
  File "<frozen runpy>", line 189, in _run_module_as_main
  File "<frozen runpy>", line 112, in _get_module_details
  File "/home/runner/work/xseller-ai-automation/xseller-ai-automation/backend/app/__init__.py", line 1, in <module>
    from agents.checks.router import should_offload, offload_to_gemini
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'agents'
```

**Root Cause**:
- Workflow executes `python -m app.jobs.m01_daily_batch` from `backend/` directory
- Python's working directory is `backend/`
- `agents/` module is in parent directory (repository root)
- Python cannot resolve `agents.checks.router` import

**Recommended Fix**: ✅ **IMPLEMENTED**
```yaml
# Before (BROKEN):
- name: Run M01 daily batch
  working-directory: backend
  run: |
    python -m app.jobs.m01_daily_batch ...

# After (FIXED):
- name: Run M01 daily batch
  run: |
    export PYTHONPATH="${GITHUB_WORKSPACE}"
    python -m backend.app.jobs.m01_daily_batch ...
```

**Why This Works**:
- Sets PYTHONPATH to repository root
- Python can now resolve both `backend.*` and `agents.*` imports
- Removes `working-directory: backend` directive
- Uses fully qualified module path `backend.app.jobs.m01_daily_batch`

---

#### **Issue #2: Missing BACKEND_API_BASE_URL Secret** 🔴

**Environment Variable**: `BACKEND_API_BASE_URL`

**Current Value**: `""` (empty string)

**Expected Value**: Backend API base URL (e.g., `https://api.xseller.ai`)

**Impact**:
- M01 job receives empty base URL
- API calls to `/api/news/ingest` and `/api/news/rank` fail
- Workflow exits with error code 1

**Exact Error (would occur after fixing Issue #1)**:
```python
# m01_daily_batch.py line 71-73
url = f"{base_url.rstrip('/')}/api/news/ingest"
# Results in: url = "/api/news/ingest" (no host!)
requests.post(url, ...)  # Connection error
```

**Recommended Fix**: ❌ **REQUIRES MANUAL ACTION**

**Steps to Fix**:

1. Go to GitHub repository settings:
   ```
   https://github.com/gurharnimrat-xseller/xseller-ai-automation/settings/secrets/actions
   ```

2. Click "New repository secret"

3. Add secret:
   - **Name**: `BACKEND_API_BASE_URL`
   - **Value**: Your backend API URL (e.g., `https://api.xseller.ai` or `https://xseller.onrender.com`)

4. Click "Add secret"

**Verification**:
```bash
# Test the secret is accessible in workflow
gh workflow run m01_daily_batch.yml --ref main
# Check run logs for: BACKEND_API_BASE_URL=<your-url>
```

---

## 4️⃣ Can M01 Start Running Tomorrow at 9AM NZT?

### Deterministic YES/NO: **NO** ❌

### Blockers

| Blocker | Status | Solution |
|---------|--------|----------|
| Python module path issue | ✅ Fixed | This PR |
| BACKEND_API_BASE_URL secret | ❌ Not configured | Manual action required |

### Required Actions Before Go-Live

1. ✅ **Merge this PR** - Fixes Python module path
2. ❌ **Configure BACKEND_API_BASE_URL secret** - See Issue #2 above
3. ⚠️ **Verify backend API is running** - M01 needs live API endpoints:
   - `POST /api/news/ingest`
   - `POST /api/news/rank`
4. ⚠️ **Optional: Configure NEWS_API_KEY secret** - If using NewsAPI source

---

## 5️⃣ Complete Fix Patch

### Changes in This PR

#### File: `.github/workflows/m01_daily_batch.yml`

**Change 1: Install dependencies without working-directory**
```diff
-      - name: Install backend dependencies
-        working-directory: backend
-        run: |
-          python -m pip install --upgrade pip
-          pip install -r requirements.txt
+      - name: Install backend dependencies
+        run: |
+          python -m pip install --upgrade pip
+          pip install -r backend/requirements.txt
```

**Change 2: Fix Python module path and remove working-directory**
```diff
-      - name: Run M01 daily batch
-        working-directory: backend
-        run: |
-          python -m app.jobs.m01_daily_batch \
+      - name: Run M01 daily batch
+        run: |
+          export PYTHONPATH="${GITHUB_WORKSPACE}"
+          python -m backend.app.jobs.m01_daily_batch \
             --base-url "${BACKEND_API_BASE_URL}" \
             --sources "${NEWS_SOURCES}" \
             --limit-per-source "${NEWS_LIMIT_PER_SOURCE}" \
             --min-score "${MIN_SCORE}"
```

---

## 6️⃣ Post-Merge Verification Steps

After merging this PR and configuring secrets:

### Step 1: Manual Test Run
```bash
# Trigger workflow manually
gh workflow run m01_daily_batch.yml --ref main

# Watch logs
gh run watch
```

### Step 2: Verify Workflow Runs Successfully
- Check that "Install backend dependencies" completes
- Check that "Run M01 daily batch" starts
- Verify BACKEND_API_BASE_URL is not empty in logs
- Verify no ModuleNotFoundError

### Step 3: Verify API Calls Work
Check workflow logs for:
```
INFO - Triggering ingestion: {'sources': ['newsapi', 'mock'], 'limit_per_source': 20}
INFO - Ingestion complete: <N> articles fetched
INFO - Triggering ranking for <N> articles (min_score=0.6)
INFO - Ranking complete: <N> articles ranked
INFO - M01 Daily Batch - Complete
```

### Step 4: Verify Schedule
- Next scheduled run: Tomorrow at 20:00 UTC (9AM NZT)
- Monitor GitHub Actions tab for automatic execution

---

## 7️⃣ Summary of Required Actions

### Immediate (This PR)
- ✅ Fix Python module path in workflow
- ✅ Update dependency installation path

### Before Go-Live (Your Actions)
- ❌ Configure `BACKEND_API_BASE_URL` secret in GitHub
- ⚠️ Optional: Configure `NEWS_API_KEY` if using NewsAPI
- ⚠️ Verify backend API endpoints are live and accessible

### Monitoring (Post-Deploy)
- 🔍 Check workflow runs daily
- 🔍 Monitor for API failures
- 🔍 Review ingestion/ranking metrics

---

## 8️⃣ Confirmation Checklist

**System Status**: Can M01 run autonomously tomorrow?

- ✅ M01 workflow file exists and is active
- ✅ Schedule is correct (9AM NZT)
- ✅ No workflow conflicts
- ✅ Python module path issue fixed (this PR)
- ❌ BACKEND_API_BASE_URL configured (ACTION REQUIRED)
- ⚠️ Backend API endpoints verified (RECOMMENDED)
- ⚠️ NEWS_API_KEY configured (OPTIONAL)

**Final Status**: 🛑 **NOT READY** - 1 required action remains

---

## 🔥 READY / NOT READY Summary

### 🔥 NOT READY

M01 Daily Batch **cannot** start running tomorrow at 9AM NZT without your intervention.

### ✅ What's Fixed
- Python module import path ✅
- Workflow file structure ✅
- No workflow conflicts ✅

### ❌ What's Blocking
- `BACKEND_API_BASE_URL` secret must be configured manually

### 🎛️ Confirmation for Autonomous Operation

**After you configure the BACKEND_API_BASE_URL secret:**
- ✅ M01 will run automatically every day at 9AM NZT
- ✅ No further intervention required
- ✅ Workflow is idempotent (safe to retry)
- ✅ Logs available in GitHub Actions tab

---

## 📝 Additional Notes

### Secret Variables Used by M01

| Secret | Required | Purpose | Default |
|--------|----------|---------|---------|
| `BACKEND_API_BASE_URL` | ✅ Yes | Backend API endpoint | None |
| `NEWS_API_KEY` | ⚠️ Conditional | NewsAPI access (if using newsapi source) | None |
| `GEMINI_API_KEY` | ⚠️ Conditional | LLM ranking (set in backend) | None |

### Environment Variables (Workflow Level)

| Variable | Value | Purpose |
|----------|-------|---------|
| `NEWS_SOURCES` | `newsapi,mock` | Which sources to ingest from |
| `NEWS_LIMIT_PER_SOURCE` | `20` | Max articles per source |
| `MIN_SCORE` | `0.6` | Minimum ranking threshold |

### Troubleshooting

**If M01 still fails after fixes:**

1. **Check secret configuration**:
   ```bash
   # Secrets are masked in logs, but you'll see:
   # BACKEND_API_BASE_URL=***
   ```

2. **Verify backend API health**:
   ```bash
   curl https://your-backend-url/api/health
   ```

3. **Test locally**:
   ```bash
   cd /path/to/repo
   export PYTHONPATH="$(pwd)"
   python -m backend.app.jobs.m01_daily_batch \
     --base-url "https://your-backend-url" \
     --sources "mock" \
     --limit-per-source 5 \
     --min-score 0.6
   ```

4. **Check workflow logs**:
   ```bash
   gh run list --workflow=m01_daily_batch.yml
   gh run view <run-id> --log
   ```

---

**Report Generated By**: GitHub Copilot SWE Agent  
**Diagnostic Timestamp**: 2025-11-13T22:54:12Z  
**Repository**: gurharnimrat-xseller/xseller-ai-automation  
**Branch**: copilot/consolidate-verify-guardrails
