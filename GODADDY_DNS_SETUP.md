# GoDaddy Domain DNS Setup for app.xseller.ai

This guide walks you through configuring your GoDaddy domain for deployment.

---

## 🎯 Deployment Architecture

```
User → app.xseller.ai → Vercel (Frontend)
                        ↓
User → api.xseller.ai → Railway/Render (Backend API)
```

---

## 📝 Step-by-Step GoDaddy DNS Configuration

### Step 1: Access GoDaddy DNS Management

1. Log into your **GoDaddy account** at [godaddy.com](https://godaddy.com)
2. Go to "My Products"
3. Find **xseller.ai** domain
4. Click "DNS" or "Manage DNS"

You'll see the DNS management page with current records.

---

### Step 2: Deploy Your Backend First

**Why?** You need the backend domain to configure the CNAME record.

#### Deploy to Railway (Recommended):

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create new project → "Deploy from GitHub"
4. Select your repository
5. Select `backend` as root directory
6. Add PostgreSQL database
7. Configure environment variables
8. Get your Railway domain (e.g., `xseller-production.up.railway.app`)

#### Deploy to Render (Alternative):

1. Go to [render.com](https://render.com)
2. Create Web Service
3. Connect GitHub repo
4. Get your Render domain (e.g., `xseller-backend.onrender.com`)

---

### Step 3: Configure API Subdomain (api.xseller.ai)

In GoDaddy DNS Management:

**Add CNAME Record:**

| Type | Name | Value | TTL |
|------|------|-------|-----|
| CNAME | api | your-backend-domain.com | 1 Hour |

**Example:**
- If Railway domain: `xseller-production.up.railway.app`
- If Render domain: `xseller-backend.onrender.com`

**Note:** Don't include `https://` - just the domain!

---

### Step 4: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Import your repository
4. Set root directory to `frontend`
5. Add environment variable:
   - `NEXT_PUBLIC_API_URL=https://api.xseller.ai`
6. Click "Deploy"

---

### Step 5: Configure App Subdomain (app.xseller.ai)

#### Option A: Vercel Provides IP Address (A Record)

Vercel might give you an IP address. If so:

**Add A Record:**
| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | app | 76.76.21.21 | 1 Hour |

#### Option B: Vercel Provides Domain (CNAME - Recommended)

Most common! Vercel gives you a domain like `your-app.vercel.app`:

**Add CNAME Record:**
| Type | Name | Value | TTL |
|------|------|-------|-----|
| CNAME | app | your-app.vercel.app | 1 Hour |

---

### Step 6: Add Custom Domain in Vercel

1. Go to Vercel Dashboard → Your Project
2. Click "Settings" → "Domains"
3. Enter: `app.xseller.ai`
4. Click "Add"

**Vercel will verify the DNS** - this can take a few minutes to 48 hours.

---

### Step 7: Add Custom Domain in Railway/Render

#### Railway:
1. Go to your service → "Settings"
2. Click "Networking"
3. Click "Custom Domain"
4. Enter: `api.xseller.ai`
5. Verify DNS

#### Render:
1. Go to your service → "Custom Domains"
2. Enter: `api.xseller.ai`
3. Copy DNS settings
4. Update GoDaddy with those settings

---

## 📋 Complete DNS Records Summary

After configuration, your GoDaddy DNS should have:

```
Type   | Name | Value                          | TTL
-------|------|--------------------------------|-------
A      | @    | Your main domain IP (existing) | 1 Hour
CNAME  | www  | xseller.ai (existing)          | 1 Hour
CNAME  | app  | your-app.vercel.app            | 1 Hour
CNAME  | api  | your-backend.railway.app       | 1 Hour
```

---

## ⏱️ DNS Propagation Time

- **Typical**: 5-30 minutes
- **Maximum**: 24-48 hours (GoDaddy)
- **Check**: Use [whatsmydns.net](https://whatsmydns.net)

---

## ✅ Verification Steps

### 1. Check DNS Propagation

Visit [whatsmydns.net](https://whatsmydns.net) and check:
- `app.xseller.ai` - should show Vercel IP
- `api.xseller.ai` - should show Railway/Render IP

### 2. Test Backend API

```bash
curl https://api.xseller.ai/
# Should return: {"message": "Xseller.ai API", "status": "running"}
```

### 3. Test Frontend

Visit: `https://app.xseller.ai` in browser

Should load without errors!

### 4. Check Browser Console

Press F12 → Console tab
- Should see NO CORS errors
- API calls should succeed

---

## 🔧 GoDaddy Common Issues

### Issue 1: "DNS Already Exists"
**Solution:** Look for existing records and delete/update them

### Issue 2: "Can't Add CNAME for Root Domain"
**Problem:** You can't have CNAME on root (@)
**Solution:** Use A record or contact GoDaddy support

### Issue 3: DNS Not Propagating
**Solution:** 
- Wait 24-48 hours
- Clear DNS cache: `ipconfig /flushdns` (Windows) or `sudo dscacheutil -flushcache` (Mac)
- Use different DNS resolver: 8.8.8.8 (Google) or 1.1.1.1 (Cloudflare)

### Issue 4: "Domain Not Verified"
**Solution:** Make sure DNS records match exactly what Vercel/Railway requires

---

## 🔐 SSL Certificate

**Automatic SSL is provided by:**
- ✅ Vercel (Let's Encrypt)
- ✅ Railway (Automatic)
- ✅ Render (Automatic)

No manual SSL setup needed! Just wait for DNS verification.

---

## 📊 Quick Reference

### Vercel DNS Settings

After adding domain in Vercel, they'll show you one of:

**Option A - A Record:**
```
Type: A
Name: app
Value: 76.76.21.21
```

**Option B - CNAME (Common):**
```
Type: CNAME
Name: app
Value: cname.vercel-dns.com
```

### Railway DNS Settings

```
Type: CNAME
Name: api
Value: your-production.up.railway.app
```

### Render DNS Settings

They'll give you specific values:
```
Type: CNAME
Name: api
Value: your-backend.onrender.com
```

---

## 🎯 Current Status Tracking

After adding DNS records, track:

1. ✅ DNS Propagation: [whatsmydns.net](https://whatsmydns.net)
2. ✅ Vercel Domain Status: Dashboard → Settings → Domains
3. ✅ Railway/Render Domain Status: Service Settings
4. ✅ SSL Status: Check HTTPS in browser
5. ✅ API Connectivity: Test in browser console

---

## 🚨 Important Notes

1. **Delete old test records** if you added any
2. **Use CNAME whenever possible** (easier to manage)
3. **Wait for propagation** before testing
4. **Check both HTTP and HTTPS** work
5. **Keep GoDaddy DNS login** handy for changes

---

## 💡 Pro Tips

1. **Test locally first** before DNS changes
2. **Keep GoDaddy DNS open** in one tab, deployment platforms in others
3. **Document your DNS values** in case you need to rebuild
4. **Use screenshot** of DNS settings before changes

---

## 🆘 Need Help?

- **GoDaddy Support**: 1-480-505-8877 or chat support
- **Vercel Support**: [vercel.com/support](https://vercel.com/support)
- **Railway Support**: [railway.app/help](https://railway.app/help)
- **Render Support**: [render.com/support](https://render.com/support)

---

## 📝 Checklist

- [ ] Deployed backend to Railway/Render
- [ ] Got backend domain
- [ ] Deployed frontend to Vercel
- [ ] Got Vercel domain
- [ ] Added CNAME for api.xseller.ai
- [ ] Added CNAME/A record for app.xseller.ai
- [ ] Added domain in Vercel settings
- [ ] Added domain in Railway/Render settings
- [ ] Waited for DNS propagation
- [ ] Verified DNS with whatsmydns.net
- [ ] Tested https://app.xseller.ai loads
- [ ] Tested https://api.xseller.ai works
- [ ] No errors in browser console
- [ ] SSL certificate active (green lock)

---

Good luck! 🚀
