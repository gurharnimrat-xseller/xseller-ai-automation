# Railway Backend Deployment Guide

This guide explains how to deploy the Xseller.ai FastAPI backend to Railway and configure it for the M01 Daily Batch GitHub Action.

## 📋 Prerequisites

- Railway account (https://railway.app)
- Railway project created (e.g., "xseller.ai")
- GitHub repository access
- API keys for:
  - Gemini AI (`GEMINI_API_KEY`)
  - News API (`NEWS_API_KEY`)
  - Database (optional: `DATABASE_URL`)

## 🚀 Railway Deployment Steps

### 1. Deploy to Railway

#### Option A: Deploy from GitHub (Recommended)
1. Go to Railway dashboard: https://railway.app/dashboard
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select: `gurharnimrat-xseller/xseller-ai-automation`
4. Railway will auto-detect the `Dockerfile` in the root
5. Click **"Deploy"**

#### Option B: Deploy via Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Deploy
railway up
```

### 2. Configure Environment Variables

In Railway project settings → **Variables**, add:

#### Required Variables:
```bash
# Port (Railway auto-injects, but set as backup)
PORT=8000

# Database URL (if using Railway PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# AI Service Keys
GEMINI_API_KEY=your-gemini-api-key-here
NEWS_API_KEY=your-newsapi-key-here

# CORS Origins (optional, defaults to localhost:3000)
ALLOWED_ORIGINS=https://xseller.ai,https://app.xseller.ai
```

#### Optional Variables:
```bash
# LLM Router Configuration
MAX_TOKENS=12000
HEAVY_TIMEOUT_SEC=90
OFFLOAD_MODEL=gemini-1.5-pro-latest
```

### 3. Get Your Railway Public URL

After deployment completes:

1. Go to your Railway project dashboard
2. Click on your service (e.g., "xseller-ai-automation")
3. Go to **Settings** tab
4. Scroll to **"Networking"** section
5. Click **"Generate Domain"** if not already generated
6. Copy the public URL, it will look like:
   ```
   https://xseller-ai-automation-production.up.railway.app
   ```
   OR
   ```
   https://xseller-ai-automation-xsellerai.up.railway.app
   ```

**Important**: Your Railway URL is your `BACKEND_API_BASE_URL`

### 4. Configure GitHub Actions Secret

Now that you have the Railway URL, configure the GitHub Action:

1. Go to your GitHub repository:
   ```
   https://github.com/gurharnimrat-xseller/xseller-ai-automation
   ```

2. Navigate to: **Settings** → **Secrets and variables** → **Actions**

3. Click **"New repository secret"**

4. Add the secret:
   - **Name**: `BACKEND_API_BASE_URL`
   - **Value**: Your Railway URL (WITHOUT trailing slash)
   
   Example:
   ```
   https://xseller-ai-automation-production.up.railway.app
   ```

5. Click **"Add secret"**

## ✅ Verify Deployment

### 1. Check Railway Logs

In Railway dashboard:
- Click on your service
- Go to **"Deployments"** tab
- Click on the latest deployment
- Check **"View Logs"**

Look for:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [1]
INFO:     Started server process [7]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2. Test Health Endpoint

Open in browser or use curl:
```bash
curl https://YOUR-RAILWAY-URL.up.railway.app/api/health
```

Expected response:
```json
{
  "api": "healthy",
  "database": "connected",
  "scheduler": "running"
}
```

### 3. Test Root Endpoint

```bash
curl https://YOUR-RAILWAY-URL.up.railway.app/
```

Expected response:
```json
{
  "message": "Xseller.ai API",
  "status": "running"
}
```

### 4. Test News Endpoints (Optional)

Test ingestion endpoint:
```bash
curl -X POST https://YOUR-RAILWAY-URL.up.railway.app/api/news/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "sources": ["mock"],
    "limit_per_source": 5
  }'
```

Expected: JSON response with `job_id`, `status`, `articles_fetched`

## 🔄 Test M01 Daily Batch Workflow

Once everything is configured:

1. Go to GitHub Actions:
   ```
   https://github.com/gurharnimrat-xseller/xseller-ai-automation/actions
   ```

2. Click on **"M01 Daily Batch"** workflow

3. Click **"Run workflow"** dropdown

4. Select branch: `main`

5. Click **"Run workflow"** button

6. Wait for the workflow to complete (~2-5 minutes)

7. Check the logs for:
   ```
   M01 Daily Batch - Starting
   Base URL: https://YOUR-RAILWAY-URL.up.railway.app
   Triggering ingestion: {...}
   Ingestion complete: X articles fetched
   Triggering ranking for X articles
   Ranking complete: X articles ranked
   M01 Daily Batch - Complete
   ```

## 🐛 Troubleshooting

### Issue: "502 Bad Gateway"

**Cause**: Backend is not running or not responding

**Solutions**:
1. Check Railway logs for errors
2. Verify environment variables are set correctly
3. Ensure `PORT` is set to `8000`
4. Check that Dockerfile is being used (not Railpack auto-detect)
5. Redeploy the service

### Issue: "No start command was found"

**Cause**: Railway couldn't detect how to start the app

**Solutions**:
1. Verify `Dockerfile` exists in repository root
2. Verify `Procfile` exists as backup
3. In Railway settings, manually set start command:
   ```
   uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
   ```

### Issue: "python3: command not found"

**Cause**: Wrong base image or missing Python

**Solution**: Verify `Dockerfile` uses `python:3.11-slim` base image

### Issue: "Module import errors" (e.g., `cannot import name 'app'`)

**Cause**: Wrong PYTHONPATH or incorrect working directory

**Solution**: 
- Dockerfile `WORKDIR` should be `/app`
- Start command should use `backend.app.main:app` (not `app.main:app`)

### Issue: M01 workflow fails with "base URL is empty"

**Cause**: `BACKEND_API_BASE_URL` secret not set or is empty

**Solution**:
1. Go to GitHub repo Settings → Secrets → Actions
2. Verify `BACKEND_API_BASE_URL` exists
3. Verify it's a valid URL starting with `https://`
4. Re-run the workflow

### Issue: "Connection timeout" or "Connection refused"

**Cause**: Railway service is sleeping or port is not exposed

**Solution**:
1. Wake the service by hitting the health endpoint
2. Check Railway settings → Networking → ensure public domain is generated
3. Verify `EXPOSE 8000` is in Dockerfile

## 📊 Cost Optimization

Railway pricing tips:
- Free tier: $5/month credit (good for development)
- Backend uses ~512MB RAM when idle
- Scale up for production: Settings → Resources → Increase memory/CPU
- Enable auto-sleep for non-production environments

## 🔐 Security Checklist

Before going to production:

- [ ] All API keys stored as Railway environment variables (never in code)
- [ ] `ALLOWED_ORIGINS` set to your frontend domains only
- [ ] Database URL uses SSL connection
- [ ] Railway project has access controls configured
- [ ] GitHub secrets have restricted access
- [ ] Railway logs don't expose sensitive data

## 📚 Additional Resources

- Railway Documentation: https://docs.railway.app
- FastAPI Deployment Guide: https://fastapi.tiangolo.com/deployment/
- Uvicorn Documentation: https://www.uvicorn.org
- GitHub Actions Secrets: https://docs.github.com/en/actions/security-guides/encrypted-secrets

## 🆘 Support

If you encounter issues:
1. Check Railway deployment logs first
2. Check GitHub Actions workflow logs
3. Verify all environment variables are set
4. Test endpoints manually with curl
5. Review this guide's troubleshooting section

---

**Last Updated**: 2025-11-15  
**Railway Service**: `xseller-ai-automation`  
**Project**: `xseller.ai`  
**Backend Entry Point**: `backend.app.main:app`  
**Port**: `8000`
