# Xseller.ai Production Deployment Guide

This guide walks you through deploying your application to `app.xseller.ai`.

## Overview

Your application consists of:
- **Frontend**: Next.js app running on port 3000
- **Backend**: FastAPI server running on port 8000
- **Database**: SQLite (needs upgrade for production)

---

## 🚀 Recommended Deployment Strategy

### Option 1: Vercel + Railway/Render (Recommended)

**Frontend → Vercel**
- Perfect for Next.js apps
- Automatic SSL certificates
- Custom domain support
- Global CDN

**Backend → Railway/Render**
- Easy Python deployments
- PostgreSQL database included
- Custom domains supported
- Auto-deploy from GitHub

### Option 2: Full Stack on One Platform

**Vercel Full Stack**
- Deploy everything on Vercel
- Use Vercel Postgres for database
- Single deployment

**DigitalOcean App Platform**
- Full-stack deployment
- Managed databases
- Simple pricing

---

## 📋 Pre-Deployment Checklist

### 1. Update Environment Variables

Create production environment files:

**Backend `.env` (Production):**
```env
DATABASE_URL=postgresql://user:password@host:5432/xseller_db
OPENAI_API_KEY=your_openai_key_here
PUBLER_API_KEY=your_publer_key_here
INVIDEO_API_KEY=your_invideo_key_here
ENVIRONMENT=production
```

### 2. Update CORS Configuration

**File: `backend/app/main.py`** (Lines 33-40)

**Replace:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**With:**
```python
# CORS configuration for production
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://app.xseller.ai,https://xseller.ai"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Remember to add:** `import os` at the top

### 3. Update Frontend API URL

**File: `frontend/lib/api.ts`** (Line 1)

**Replace:**
```javascript
const BASE_URL = 'http://localhost:8000';
```

**With:**
```javascript
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.xseller.ai';
```

### 4. Update Next.js Config

**File: `frontend/next.config.js`** already has environment variable support!

### 5. Database Upgrade (Critical!)

SQLite is not suitable for production. Switch to PostgreSQL:

**File: `backend/app/database.py`** (Line 4)

Already reads from `DATABASE_URL` environment variable ✅

**File: `backend/app/main.py`** (Line 16)

**Replace:**
```python
DATABASE_URL = "sqlite:///./xseller.db"
```

**With:**
```python
import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./xseller.db")
```

**Update `backend/requirements.txt`:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlmodel==0.0.14
apscheduler==3.10.4
openai==1.3.7
httpx==0.25.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
feedparser==6.0.10
tweepy==4.14.0
werkzeug==3.0.1
psycopg2-binary==2.9.9  # Add PostgreSQL support
```

---

## 🔵 Deployment: Vercel (Frontend)

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login
```bash
vercel login
```

### Step 3: Deploy from frontend directory
```bash
cd frontend
vercel --prod
```

### Step 4: Configure Environment Variables
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add: `NEXT_PUBLIC_API_URL=https://api.xseller.ai`

### Step 5: Add Custom Domain
1. Settings → Domains
2. Add `app.xseller.ai`
3. Follow DNS configuration instructions

---

## 🚂 Deployment: Railway (Backend)

### Step 1: Sign Up
- Go to [railway.app](https://railway.app)
- Sign up with GitHub

### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `xseller-ai-automation`
4. Select "backend" as root directory

### Step 3: Add PostgreSQL Database
1. Click "+ New" → "Database" → "PostgreSQL"
2. Railway auto-creates `DATABASE_URL` environment variable

### Step 4: Configure Environment Variables
1. Go to your service → "Variables" tab
2. Add:
   - `DATABASE_URL` (auto-generated)
   - `OPENAI_API_KEY=your_key`
   - `PUBLER_API_KEY=your_key`
   - `INVIDEO_API_KEY=your_key`
   - `ALLOWED_ORIGINS=https://app.xseller.ai`

### Step 5: Configure Build Settings
1. Go to "Settings" → "Deploy"
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 6: Add Custom Domain
1. "Settings" → "Networking"
2. Generate Domain
3. Click "Custom Domain" → Add `api.xseller.ai`
4. Follow DNS instructions

---

## 🔄 Alternative: Render Deployment

### Backend on Render

1. **Create Web Service**
   - Connect GitHub repository
   - Root directory: `backend`

2. **Configure:**
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Add PostgreSQL:**
   - Create PostgreSQL database
   - Use connection string as `DATABASE_URL`

4. **Environment Variables:**
   - Add all API keys and CORS origins

5. **Custom Domain:**
   - Add `api.xseller.ai`

---

## 🌐 DNS Configuration

Configure your domain (`xseller.ai`) DNS records:

### Cloudflare Example:

1. **A Record** for `app.xseller.ai`:
   - Type: `A`
   - Name: `app`
   - Value: Vercel IP (provided by Vercel)
   - TTL: Auto

2. **CNAME** for `api.xseller.ai`:
   - Type: `CNAME`
   - Name: `api`
   - Value: Railway/Render provided domain
   - Proxy: Off (gray cloud)

### Domain Provider Example:

**If using Namecheap, GoDaddy, etc:**
- Add A record for `app` subdomain pointing to Vercel IP
- Add CNAME for `api` subdomain pointing to Railway/Render domain

---

## 🔐 SSL Certificates

**Automatic SSL:**
- Vercel: Automatic Let's Encrypt certificates ✅
- Railway: Automatic SSL ✅
- Render: Automatic SSL ✅

No manual configuration needed!

---

## ✅ Post-Deployment Checklist

1. ✅ Test `https://app.xseller.ai` loads
2. ✅ Test API calls work from frontend
3. ✅ Verify database connection
4. ✅ Check CORS headers in browser console
5. ✅ Test scheduled jobs (if applicable)
6. ✅ Monitor error logs

---

## 🐛 Troubleshooting

### CORS Errors
- Verify `ALLOWED_ORIGINS` includes your frontend URL
- Check backend logs for CORS middleware

### API Connection Errors
- Verify `NEXT_PUBLIC_API_URL` environment variable
- Check backend is accessible via `api.xseller.ai`

### Database Errors
- Verify PostgreSQL connection string
- Check database migrations ran successfully
- Review database logs in Railway/Render dashboard

### 404 on Refresh (Next.js)
- This is normal for SPA routing
- Vercel handles this automatically ✅

---

## 📊 Monitoring

### Recommended Tools:

1. **Vercel Analytics** - Frontend performance
2. **Railway Metrics** - Backend health
3. **Sentry** - Error tracking
4. **LogRocket** - User session replay

---

## 💰 Cost Estimation

**Vercel:**
- Hobby Plan: Free (personal projects)
- Pro Plan: $20/month (team features)

**Railway:**
- Trial: $5 free credit
- Estimate: $5-15/month for small apps

**Render:**
- Free tier available
- Paid: $7/month per service

**Total Estimate: $0-30/month** for a small-medium deployment

---

## 🎯 Next Steps

1. Choose deployment platform
2. Make configuration changes above
3. Deploy backend first
4. Deploy frontend with API URL
5. Configure DNS
6. Test thoroughly
7. Set up monitoring

---

## 📞 Need Help?

- Vercel Docs: https://vercel.com/docs
- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs

Good luck! 🚀

