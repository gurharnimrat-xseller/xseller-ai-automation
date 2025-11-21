# Vercel Deployment Guide for Xseller.ai Dashboard

## Prerequisites
Fix npm permissions first (one-time):
```bash
sudo chown -R $(whoami) ~/.npm
```

## Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

## Step 2: Login to Vercel
```bash
vercel login
# This opens browser for authentication
```

## Step 3: Deploy to Production
```bash
cd frontend
vercel --prod --yes
```

When prompted:
- Set up and deploy? → **Y**
- Link to existing project? → **N**
- Project name? → **xseller-ai-dashboard**
- Directory? → **./**
- Override settings? → **N**

## Step 4: Set Environment Variable
In Vercel Dashboard (https://vercel.com/dashboard):
1. Select your project
2. Go to Settings → Environment Variables
3. Add:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://strong-encouragement-xsellerai.up.railway.app`
   - Environment: Production

Or via CLI:
```bash
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://strong-encouragement-xsellerai.up.railway.app
```

## Step 5: Redeploy with Environment Variables
```bash
vercel --prod --yes
```

## Step 6: Add Custom Domain
```bash
vercel domains add app.xseller.ai
```

Or in Vercel Dashboard:
1. Go to Settings → Domains
2. Click "Add Domain"
3. Enter: `app.xseller.ai`

---

# DNS Configuration for app.xseller.ai

## Option 1: CNAME Record (Recommended)
Add this DNS record at your domain registrar:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| CNAME | app | cname.vercel-dns.com | 3600 |

## Option 2: A Record
If CNAME doesn't work:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | app | 76.76.21.21 | 3600 |

## DNS Propagation
- Takes 10-60 minutes
- Check status: https://dnschecker.org/#CNAME/app.xseller.ai

---

## Verification Checklist

After deployment:
- [ ] Visit https://xseller-ai-dashboard.vercel.app (Vercel URL)
- [ ] Verify dashboard loads
- [ ] Check API calls work (no CORS errors)
- [ ] Wait for DNS propagation
- [ ] Visit https://app.xseller.ai
- [ ] Verify custom domain works

## Troubleshooting

### CORS Errors
Backend already configured to allow:
- `http://localhost:3000`
- `https://app.xseller.ai`
- `https://xseller-ai-dashboard.vercel.app`

### Environment Variable Not Working
1. Check it's set for "Production" environment
2. Redeploy after adding: `vercel --prod`

### Domain Not Working
1. Verify DNS records are correct
2. Check propagation: https://dnschecker.org
3. In Vercel, check domain shows "Valid Configuration"
