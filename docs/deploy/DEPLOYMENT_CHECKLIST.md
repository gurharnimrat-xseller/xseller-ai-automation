# 🚀 Railway Backend Deployment Checklist

Use this checklist to deploy and verify the Xseller.ai backend on Railway.

## Pre-Deployment

- [ ] Railway account created and logged in
- [ ] GitHub repository access confirmed
- [ ] API keys obtained:
  - [ ] `GEMINI_API_KEY`
  - [ ] `NEWS_API_KEY`
  - [ ] `DATABASE_URL` (if using external database)

## Step 1: Railway Project Setup

- [ ] Create new Railway project or use existing
- [ ] Connect GitHub repository: `gurharnimrat-xseller/xseller-ai-automation`
- [ ] Verify Dockerfile is detected by Railway
- [ ] Initial deployment triggered

## Step 2: Environment Variables Configuration

Set these in Railway → Project → Variables:

### Required:
- [ ] `PORT=8000`
- [ ] `GEMINI_API_KEY=<your-key>`
- [ ] `NEWS_API_KEY=<your-key>`

### Optional but Recommended:
- [ ] `DATABASE_URL=<database-connection-string>`
- [ ] `ALLOWED_ORIGINS=https://yourdomain.com`
- [ ] `MAX_TOKENS=12000`
- [ ] `HEAVY_TIMEOUT_SEC=90`

## Step 3: Generate Public URL

- [ ] Go to Railway → Settings → Networking
- [ ] Click "Generate Domain"
- [ ] Copy the generated URL (e.g., `https://xseller-ai-automation-production.up.railway.app`)
- [ ] Save this URL - it's your `BACKEND_API_BASE_URL`

## Step 4: GitHub Actions Secret Configuration

- [ ] Go to GitHub repo → Settings → Secrets and variables → Actions
- [ ] Click "New repository secret"
- [ ] Name: `BACKEND_API_BASE_URL`
- [ ] Value: Your Railway URL (NO trailing slash)
- [ ] Click "Add secret"

## Step 5: Deployment Verification

### Check Railway Logs:
- [ ] Deployment succeeded (green checkmark)
- [ ] Logs show: `Uvicorn running on http://0.0.0.0:8000`
- [ ] No error messages in logs

### Test Endpoints:

Run these commands (replace `YOUR-URL` with your Railway URL):

```bash
# 1. Root endpoint
curl https://YOUR-URL.up.railway.app/

# Expected: {"message": "Xseller.ai API", "status": "running"}
```
- [ ] Root endpoint responding

```bash
# 2. Health endpoint
curl https://YOUR-URL.up.railway.app/api/health

# Expected: {"api": "healthy", "database": "connected", "scheduler": "running"}
```
- [ ] Health endpoint responding

```bash
# 3. Test ingestion (optional)
curl -X POST https://YOUR-URL.up.railway.app/api/news/ingest \
  -H "Content-Type: application/json" \
  -d '{"sources": ["mock"], "limit_per_source": 5}'

# Expected: JSON with job_id, status, articles_fetched
```
- [ ] Ingestion endpoint responding (optional test)

## Step 6: M01 Daily Batch Workflow Test

- [ ] Go to GitHub Actions → M01 Daily Batch
- [ ] Click "Run workflow"
- [ ] Select branch: `main`
- [ ] Click "Run workflow" button
- [ ] Wait for workflow to complete (~2-5 minutes)
- [ ] Verify logs show:
  - `M01 Daily Batch - Starting`
  - `Base URL: https://YOUR-URL...`
  - `Calling endpoint: POST https://YOUR-URL.../api/news/ingest`
  - `Ingestion complete: X articles fetched`
  - `Calling endpoint: POST https://YOUR-URL.../api/news/rank`
  - `Ranking complete: X articles ranked`
  - `M01 Daily Batch - Complete`

## Troubleshooting

If any step fails, refer to:
- 📘 `docs/deploy/railway_backend.md` - Full deployment guide
- 🔍 Railway deployment logs
- 📊 GitHub Actions workflow logs

### Common Issues:

**502 Bad Gateway:**
- Check Railway logs for errors
- Verify environment variables are set
- Ensure service is running

**M01 workflow fails:**
- Verify `BACKEND_API_BASE_URL` secret is set in GitHub
- Check that URL doesn't have trailing slash
- Verify Railway backend is running

**Module import errors:**
- Check Dockerfile is using `python:3.11-slim`
- Verify WORKDIR is `/app`
- Ensure start command uses `backend.app.main:app`

## Post-Deployment

- [ ] Document your Railway URL in team wiki/docs
- [ ] Set up monitoring/alerts (optional)
- [ ] Schedule regular M01 Daily Batch runs (already configured in workflow)
- [ ] Review Railway logs periodically for errors

## Production Checklist (Before Going Live)

- [ ] Enable Railway auto-scaling
- [ ] Set up custom domain (optional)
- [ ] Configure SSL certificates (automatic on Railway)
- [ ] Set `ALLOWED_ORIGINS` to production domains only
- [ ] Review and limit Railway project access
- [ ] Set up database backups
- [ ] Enable Railway metrics and monitoring
- [ ] Test failover scenarios
- [ ] Document incident response procedures

---

**Deployment Date**: _____________  
**Deployed By**: _____________  
**Railway URL**: _____________  
**Environment**: Production / Staging / Development
