# 🚀 Quick Start Guide - Get M01 Running in 5 Minutes

## Current Status: NOT READY ❌

M01 **cannot** run autonomously until you complete **1 required action**.

---

## ✅ What's Fixed (No Action Needed)

- ✅ Python module path issue - **FIXED in this PR**
- ✅ Workflow dependencies - **NO CONFLICTS**
- ✅ Schedule configuration - **CORRECT (9AM NZT)**

---

## ❌ What You Must Do (1 Required Action)

### Configure BACKEND_API_BASE_URL Secret

**Time Required**: 2 minutes

#### Steps:

1. **Go to your repository settings**:
   ```
   https://github.com/gurharnimrat-xseller/xseller-ai-automation/settings/secrets/actions
   ```

2. **Click**: "New repository secret"

3. **Fill in**:
   - **Name**: `BACKEND_API_BASE_URL`
   - **Value**: Your backend API URL
     - Example: `https://api.xseller.ai`
     - Example: `https://xseller-backend.onrender.com`
     - Example: `http://localhost:8000` (for testing)

4. **Click**: "Add secret"

5. **Done!** ✅

---

## 🧪 Testing After Setup

### Test the workflow manually:

```bash
# Trigger the workflow
gh workflow run m01_daily_batch.yml --ref main

# Watch it run
gh run watch
```

### Expected output in logs:

```
✅ INFO - M01 Daily Batch - Starting
✅ INFO - Base URL: https://your-backend-url
✅ INFO - Sources: ['newsapi', 'mock']
✅ INFO - Triggering ingestion: {...}
✅ INFO - Ingestion complete: N articles fetched
✅ INFO - Triggering ranking for N articles
✅ INFO - Ranking complete: N articles ranked
✅ INFO - M01 Daily Batch - Complete
```

---

## 📅 Automatic Schedule

After you configure the secret, M01 will run automatically:

- **Frequency**: Daily
- **Time**: 9:00 AM NZT (20:00 UTC previous day)
- **Next Run**: Tomorrow morning

---

## ⚠️ Optional (But Recommended)

### 1. Verify Backend is Running

```bash
# Test your backend API
curl https://your-backend-url/health
curl https://your-backend-url/api/news/articles/pending
```

### 2. Configure NewsAPI Key (if using NewsAPI source)

If you want to use NewsAPI (not just mock data):

1. Go to repository secrets
2. Add secret:
   - **Name**: `NEWS_API_KEY`
   - **Value**: Your NewsAPI key from https://newsapi.org

---

## 📊 Monitoring

### View workflow runs:

```bash
# List recent runs
gh run list --workflow=m01_daily_batch.yml

# View specific run
gh run view <run-id> --log
```

### Or use GitHub UI:

```
https://github.com/gurharnimrat-xseller/xseller-ai-automation/actions/workflows/m01_daily_batch.yml
```

---

## 🔥 Ready Checklist

- [x] Merge this PR (fixes Python module path)
- [ ] Configure `BACKEND_API_BASE_URL` secret ⚠️ **DO THIS NOW**
- [ ] Test manually (recommended)
- [ ] Verify backend is accessible (recommended)
- [ ] Wait for tomorrow's automatic run 🎉

---

## 🆘 Troubleshooting

### Problem: Workflow still fails after setup

**Check**:
1. Is `BACKEND_API_BASE_URL` secret configured?
2. Is the URL correct (no trailing slash)?
3. Is your backend API running and accessible?
4. Do the API endpoints exist (`/api/news/ingest`, `/api/news/rank`)?

**Debug**:
```bash
# Test backend directly
curl -X POST https://your-backend-url/api/news/ingest \
  -H "Content-Type: application/json" \
  -d '{"sources": ["mock"], "limit_per_source": 5}'
```

### Problem: "No module named 'agents'" error

This PR fixes this issue. Make sure you've merged the PR.

### Problem: Can't find workflow in GitHub Actions

The workflow file is: `.github/workflows/m01_daily_batch.yml`

Verify it exists:
```bash
ls -la .github/workflows/m01_daily_batch.yml
```

---

## 📖 Full Documentation

For complete diagnostic details, see: `M01_DIAGNOSTIC_REPORT.md`

---

**That's it!** Configure the secret and M01 will run automatically every morning. 🎉
