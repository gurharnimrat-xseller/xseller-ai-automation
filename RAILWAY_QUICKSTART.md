# Railway Deployment - Quick Start Guide

**Get your backend running on Railway in 5 minutes!**

## 🎯 What You Need

1. Railway account: https://railway.app
2. This repository connected to Railway
3. Your API keys ready

## ⚡ Quick Deploy Steps

### 1. Deploy to Railway (2 minutes)

```bash
# Option A: Via Railway Dashboard
1. Go to https://railway.app/dashboard
2. Click "New Project" → "Deploy from GitHub repo"
3. Select: gurharnimrat-xseller/xseller-ai-automation
4. Wait for deployment (~2 minutes)

# Option B: Via Railway CLI
railway up
```

### 2. Set Environment Variables (1 minute)

In Railway Dashboard → Your Project → Variables, add:

```env
PORT=8000
GEMINI_API_KEY=your_gemini_key_here
NEWS_API_KEY=your_newsapi_key_here
```

### 3. Get Your Public URL (30 seconds)

1. Railway Dashboard → Settings → Networking
2. Click "Generate Domain"
3. **Copy this URL** (e.g., `https://xseller-ai-automation-production.up.railway.app`)

### 4. Configure GitHub Secret (1 minute)

1. Go to: https://github.com/gurharnimrat-xseller/xseller-ai-automation/settings/secrets/actions
2. Click "New repository secret"
3. Name: `BACKEND_API_BASE_URL`
4. Value: Your Railway URL (from step 3, NO trailing slash)
5. Click "Add secret"

### 5. Test It! (30 seconds)

```bash
# Replace YOUR-URL with your actual Railway URL
curl https://YOUR-URL.up.railway.app/api/health
```

Expected response:
```json
{"api": "healthy", "database": "connected", "scheduler": "running"}
```

✅ **Done!** Your backend is now live on Railway.

## 🧪 Test M01 Daily Batch

1. Go to: https://github.com/gurharnimrat-xseller/xseller-ai-automation/actions
2. Click "M01 Daily Batch" workflow
3. Click "Run workflow" → Run
4. Wait ~2 minutes
5. Check logs for success message

## 📚 More Information

- **Full Guide**: `docs/deploy/railway_backend.md`
- **Checklist**: `docs/deploy/DEPLOYMENT_CHECKLIST.md`
- **Troubleshooting**: See the full guide

## 🆘 Something Wrong?

**502 Error?**
- Check Railway logs for errors
- Verify environment variables are set

**M01 Workflow Failing?**
- Verify `BACKEND_API_BASE_URL` is set in GitHub secrets
- Ensure URL has no trailing slash

**Need Help?**
- Check Railway deployment logs
- Review `docs/deploy/railway_backend.md`

---

**Backend Port**: 8000  
**App Entry Point**: `backend.app.main:app`  
**Health Check**: `/api/health`  
**M01 Endpoints**: `/api/news/ingest`, `/api/news/rank`
