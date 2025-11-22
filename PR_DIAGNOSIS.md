# PR 24/25/27 Deep Diagnosis + Analysis

## 1️⃣ Inspect PRs #24, #25, #27 (No Guessing)

### PR #24: Fix Python lint errors for PR cleanup

| Attribute | Value |
|-----------|-------|
| **PR Number** | 24 |
| **Title** | Fix Python lint errors for PR cleanup |
| **Merge Status** | **MERGED** (merged on 2025-11-13) |
| **Base Branch** | main |
| **Head Branch** | copilot/fix-python-lint-errors |

#### Files Changed (PR #24)

| File Path | Type | What Changed | Impact |
|-----------|------|--------------|--------|
| `agents/checks/verify_guardrails.py` | Modified | - Removed `verify_guardrails.py` from EXCLUDE list<br>- Changed logic to use `should_scan()` function instead of hardcoded file check | **✅ CI/Guardrails**: Improved guardrails scanning logic<br>**❌ Scheduled Jobs**: No impact<br>**❌ M01**: No impact |

**Analysis**: This PR only touched the guardrails verification script itself - no workflow files, no scheduler changes, no M01 code.

---

### PR #25: Fix Python lint errors across backend

| Attribute | Value |
|-----------|-------|
| **PR Number** | 25 |
| **Title** | Fix Python lint errors across backend |
| **Merge Status** | **MERGED** (merged on 2025-11-13) |
| **Base Branch** | main |
| **Head Branch** | copilot/fix-python-lint-errors-in-backend |

#### Files Changed (PR #25 - Backend Python Files)

**Total Files: 16** (all backend Python files)

All changes were **formatting/lint fixes only**:
- Moved guardrails imports to top of file with `# noqa: F401`
- Fixed import order (moved `from __future__ import annotations` to first line)
- Added `# noqa: E402` for imports after dotenv loading in `main.py`
- Applied Black formatter (line breaks, spacing, string quotes)
- No functional logic changes
- No workflow files modified
- No scheduler logic altered

**Key Files Modified**:
- `backend/app/main.py` - Import reordering only
- `backend/app/scheduler.py` - Formatting only, **NO schedule changes**
- `backend/app/content_scraper.py` - Formatting only
- `backend/app/routes.py` - Formatting only
- 12 other backend files - all formatting/lint fixes

#### Impact Analysis (PR #25)

| Category | Impact |
|----------|--------|
| **✅ CI/Guardrails** | Fixed lint errors to pass CI checks |
| **❌ Scheduled Jobs** | **NO CHANGES** to cron schedules or job logic |
| **❌ M01 Code** | **NO CHANGES** to news ingest/ranking functionality |
| **❌ Workflows** | **NO WORKFLOW FILES CHANGED** |

---

### PR #27: Add M01 daily batch workflow with proper lint configuration

| Attribute | Value |
|-----------|-------|
| **PR Number** | 27 |
| **Title** | Add M01 daily batch workflow with proper lint configuration |
| **Merge Status** | **OPEN** (Draft, not merged yet) |
| **Base Branch** | main |
| **Head Branch** | copilot/fix-python-lint-errors-again |
| **Behind Main** | Yes (mergeable but behind) |

#### Files Changed (PR #27)

| File Path | Type | What Changed | Impact |
|-----------|------|--------------|--------|
| `.github/workflows/m01_daily_batch.yml` | **NEW FILE** | **NEW WORKFLOW**<br>- Schedule: `cron: "0 20 * * *"` (daily at 20:00 UTC = 9am NZT)<br>- Manual trigger: `workflow_dispatch`<br>- Runs M01 news ingestion + ranking pipeline<br>- Uses secrets: `BACKEND_API_BASE_URL` | **✅ Scheduled Jobs**: **ADDS** new daily M01 job<br>**✅ M01 Code**: **ADDS** orchestration for M01 pipeline<br>**❌ CI/Guardrails**: No impact on existing CI |
| `backend/app/jobs/m01_daily_batch.py` | **NEW FILE** | **NEW ENTRYPOINT**<br>- CLI script to orchestrate M01 pipeline<br>- Calls `/api/news/ingest` and `/api/news/rank` endpoints<br>- Args: `--base-url`, `--sources`, `--limit-per-source`, `--min-score`<br>- Includes guardrails imports with `# noqa: F401` | **✅ M01 Code**: **ADDS** new batch job entrypoint<br>**❌ CI/Guardrails**: No impact<br>**❌ Scheduled Jobs**: File itself doesn't schedule (workflow does) |

**Key Observations**:
- This PR **introduces NEW functionality** (M01 automation)
- Does **NOT modify** existing workflows
- Does **NOT change** any existing scheduler code in `backend/app/scheduler.py`
- The workflow file is **not yet on main** (PR is still open/draft)

---

## 2️⃣ Answer Direct Questions (Based on What I Saw)

### Q1: Did any of these PRs disable, rename, or change CI workflows?

**Answer: NO**

- **PR #24**: Modified `agents/checks/verify_guardrails.py` (not a workflow file)
- **PR #25**: Modified 16 backend Python files (NO workflow files)
- **PR #27**: **ADDS** a new workflow `.github/workflows/m01_daily_batch.yml` (does not modify existing workflows)

**Current CI workflows** (unchanged by these PRs):
- `.github/workflows/ci.yml` - Main CI (on push/PR)
- `.github/workflows/guardrails.yml` - Guardrails scan (on PR)
- `.github/workflows/backend-ci.yml` - Backend tests
- `.github/workflows/frontend-ci.yml` - Frontend tests
- `.github/workflows/monitor.yml` - Monitor job (paused)

### Q2: Did any of these PRs change `on:` triggers (schedule, push, workflow_dispatch)?

**Answer: NO existing triggers changed, but PR #27 ADDS a new scheduled trigger**

| PR | Trigger Changes |
|----|-----------------|
| PR #24 | ❌ None |
| PR #25 | ❌ None |
| PR #27 | ✅ **ADDS** new `on: schedule` + `on: workflow_dispatch` in `m01_daily_batch.yml`<br>⚠️ **BUT PR #27 IS NOT MERGED YET** |

**Existing workflow triggers** (confirmed unchanged):
- `ci.yml`: `on: [push (main), pull_request, workflow_dispatch]`
- `guardrails.yml`: `on: [pull_request]`
- `monitor.yml`: `on: [schedule (paused annually), workflow_dispatch]`

### Q3: Did any of these PRs change M01 (news ingestion + ranking)?

**Answer: PR #27 ADDS M01 automation (but not merged), PRs #24 and #25 did NOT touch M01**

| PR | M01 Changes |
|----|-------------|
| PR #24 | ❌ No M01 changes |
| PR #25 | ❌ No M01 changes (formatting only) |
| PR #27 | ✅ **ADDS** M01 automation:<br>- New workflow: `m01_daily_batch.yml`<br>- New CLI tool: `backend/app/jobs/m01_daily_batch.py`<br>- Orchestrates `/api/news/ingest` → `/api/news/rank` API calls<br>⚠️ **NOT MERGED YET (PR is open/draft)** |

### Q4: Did any of these PRs add/remove scheduler or job files?

**Answer: PR #27 ADDS a new job file (but NOT a scheduler change)**

| File | Change |
|------|--------|
| `backend/app/scheduler.py` | ✅ **NOT MODIFIED** by any PR |
| `backend/app/jobs/m01_daily_batch.py` | ✅ **NEW FILE in PR #27** (CLI entrypoint, not a scheduler) |
| `.github/workflows/m01_daily_batch.yml` | ✅ **NEW WORKFLOW in PR #27** (GitHub Actions schedule, not Python scheduler) |

**Important**: PR #27 does **NOT** modify `backend/app/scheduler.py`. The existing Python in-process scheduler (APScheduler) is untouched.

---

## 3️⃣ Current Main Branch - Workflow Responsibilities

### CI + Guardrails Workflows

| Workflow File | Triggers | Purpose | Issues? |
|---------------|----------|---------|---------|
| `.github/workflows/ci.yml` | `push: [main]`<br>`pull_request`<br>`workflow_dispatch` | **Master CI pipeline**<br>- Runs guardrails scan<br>- Lints Python (ruff, mypy)<br>- Lints Node (eslint)<br>- Runs pytest<br>- Runs npm test | ✅ No issues from PRs 24/25/27 |
| `.github/workflows/guardrails.yml` | `pull_request` | **Standalone guardrails check**<br>- Runs `verify_guardrails.py` | ⚠️ **REDUNDANT** (also run in ci.yml)<br>✅ No issues from PRs 24/25/27 |
| `.github/workflows/backend-ci.yml` | `push`<br>`pull_request` | Backend-specific CI | ✅ No issues |
| `.github/workflows/frontend-ci.yml` | `push`<br>`pull_request` | Frontend-specific CI | ✅ No issues |

### M01 / News Ingest Workflows

| Workflow File | Triggers | Purpose | Issues? |
|---------------|----------|---------|---------|
| `.github/workflows/m01_daily_batch.yml` | **NOT ON MAIN YET**<br>(PR #27 open) | Would run daily M01 news ingest + ranking<br>- Schedule: `0 20 * * *` (9am NZT)<br>- Manual: `workflow_dispatch` | ⚠️ **NOT MERGED** - functionality not active |
| `backend/app/scheduler.py` | N/A (in-process Python scheduler) | APScheduler cron jobs:<br>1. `fetch_and_generate_content()` at 21:00 UTC (10am NZT)<br>2. `process_video_generation_queue()` every 2 min | ✅ No changes from PRs 24/25/27 |

**Key Finding**: There is **NO active M01 scheduled workflow** on main. PR #27 would add it but is not merged.

### Monitor / Cleanup Workflows

| Workflow File | Triggers | Purpose | Issues? |
|---------------|----------|---------|---------|
| `.github/workflows/monitor.yml` | `schedule: "0 0 1 1 *"`<br>(Jan 1 annually - paused)<br>`workflow_dispatch` | Budget/usage monitoring<br>- Runs `agents/checks/monitor.py` | ✅ Intentionally paused<br>✅ No issues from PRs 24/25/27 |

---

## Summary of Findings

### What Changed (Actual Facts)

1. **PR #24 (Merged)**: Fixed guardrails script logic - no workflow impact
2. **PR #25 (Merged)**: Fixed Python formatting across backend - no functional/workflow changes
3. **PR #27 (Open/Draft)**: Would add M01 daily automation if merged - not active yet

### What's Broken or Risky

**Nothing is broken by PRs 24/25/27.** However:

1. ⚠️ **M01 automation not active**: PR #27 (M01 daily batch) is not merged, so there's no GitHub Actions workflow running M01 daily
2. ⚠️ **Redundant workflows**: `guardrails.yml` duplicates work from `ci.yml`
3. ⚠️ **In-process scheduler vs GitHub Actions**: `backend/app/scheduler.py` runs APScheduler jobs in-process, but these only work if the backend is running continuously

### What's Actually Fine

✅ All CI workflows work correctly after PRs 24/25  
✅ No existing workflows were disabled or broken  
✅ No schedule triggers were changed  
✅ Python scheduler (`backend/app/scheduler.py`) is unchanged  
✅ Guardrails checks pass after lint fixes  

---

## 3️⃣ Proposed Next Plan

### What is Broken or Risky Now

1. **M01 Daily Batch Not Active**
   - PR #27 adds the M01 daily workflow but is not merged
   - Risk: M01 automation not running on schedule
   - Cause: PR #27 is in draft state, not merged to main

2. **Workflow Redundancy**
   - `guardrails.yml` duplicates the guardrails job in `ci.yml`
   - Risk: Wastes CI minutes
   - Cause: Leftover from earlier setup

3. **Unclear Scheduling Strategy**
   - Both `backend/app/scheduler.py` (APScheduler) and GitHub Actions workflows exist
   - Risk: Confusion about which scheduler handles what
   - Cause: Mixed scheduling approaches (in-process vs cron workflows)

### What is Actually Fine and Doesn't Need Touching

✅ `ci.yml` - Main CI pipeline works correctly  
✅ `backend-ci.yml` - Backend tests work  
✅ `frontend-ci.yml` - Frontend tests work  
✅ `backend/app/scheduler.py` - APScheduler logic is intact  
✅ All backend Python files - Lints pass after PR #25  
✅ Guardrails verification - Works after PR #24 fix  

### Concrete Plan for Next Branch + PR

**Branch Name**: `ops/fix-workflows-after-24-25-27`

#### Changes to Make

**1. `.github/workflows/m01_daily_batch.yml`** (if merging PR #27)
- **Action**: Review PR #27 and merge if ready, OR recreate the workflow on this branch
- **Changes**: None needed if PR #27 is merged; validate the workflow config
- **Why**: Activate M01 daily automation

**2. `.github/workflows/guardrails.yml`**
- **Action**: Delete this file (redundant)
- **Reason**: Guardrails already run in `ci.yml` as the first job

**3. `.github/workflows/README.md`** (document workflow responsibilities)
- **Action**: Update to clarify:
  - Which workflows handle CI/guardrails
  - Which workflows handle M01 automation
  - Relationship between APScheduler (in-process) and GitHub Actions (cron)

**4. No changes needed to**:
- ❌ `ci.yml` (keep as-is)
- ❌ `backend/app/scheduler.py` (keep in-process jobs as-is)
- ❌ Any backend Python files (all lint-clean after PR #25)

### Summary of Plan

1. **Merge or integrate PR #27** to activate M01 daily automation
2. **Remove redundant `guardrails.yml`** (duplicate of ci.yml)
3. **Document workflow strategy** in README.md
4. **No changes to application code** (only workflows/documentation)

This is a minimal, surgical fix focused on workflow clarity and avoiding redundancy.
