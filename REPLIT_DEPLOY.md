# Deploy Xseller.ai on Replit

This guide shows you how to deploy your full-stack Xseller.ai application on Replit with a single click!

---

## 🚀 Quick Start

### Step 1: Import to Replit

1. Go to [replit.com](https://replit.com)
2. Click "Create Repl"
3. Choose "Import from GitHub"
4. Enter: `https://github.com/gurharnimrat-xseller/xseller-ai-automation.git`
5. Click "Import"

### Step 2: Configure Environment Variables (Optional)

If you need to set environment variables:

1. Go to "Secrets" tab (🔒 icon in sidebar)
2. Add secrets:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `PUBLER_API_KEY` - Your Publer API key
   - `INVIDEO_API_KEY` - Your InVideo API key
   - `DATABASE_URL` - PostgreSQL URL (if using external DB)
   - `ALLOWED_ORIGINS` - Comma-separated list of allowed origins

### Step 3: Run the Project

Just click the **"Run"** button at the top of Replit!

The `start.sh` script will automatically:
1. ✅ Check if ports 8000 and 3000 are available
2. ✅ Set up Python virtual environment
3. ✅ Install backend dependencies
4. ✅ Start FastAPI backend on port 8000
5. ✅ Install frontend dependencies
6. ✅ Build Next.js application
7. ✅ Start frontend on port 3000

---

## 📋 How It Works

### Architecture

```
User Browser
    ↓
Replit Webview (Port 3000)
    ↓
Next.js Frontend
    ↓
Next.js Rewrite (/api/*)
    ↓
FastAPI Backend (Port 8000)
    ↓
SQLite Database
```

### Files Created

#### `start.sh`
Master startup script that:
- Creates Python venv if needed
- Installs Python dependencies
- Starts backend in background
- Waits for backend to be ready
- Installs Node.js dependencies
- Builds Next.js app
- Starts frontend server

#### `.replit`
Configuration for Replit:
- Run command: `bash start.sh`
- Python version: 3.11
- Node.js version: 20
- Environment variables
- Deployment settings

### Frontend Changes

#### `next.config.js`
Added URL rewrites to proxy API calls:
```javascript
async rewrites() {
    return [
        {
            source: '/api/:path*',
            destination: 'http://localhost:8000/api/:path*',
        },
    ];
}
```

#### `frontend/lib/api.ts`
Changed to use relative URLs:
```javascript
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';
```

This means:
- In Replit: Uses `/api/*` (proxied via rewrites)
- In production: Can use `NEXT_PUBLIC_API_URL` environment variable

---

## 🐛 Troubleshooting

### Port Already in Use

**Error:** `Port 8000 is already in use!`

**Solution:**
```bash
# Kill existing processes
pkill -f uvicorn
pkill -f node

# Then click Run again
```

### Build Fails

**Error:** `npm install` or `npm run build` fails

**Solution:**
1. Check Replit console for errors
2. Try clearing cache: `rm -rf frontend/node_modules frontend/.next`
3. Run manually:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

### Backend Not Starting

**Error:** Backend logs show errors

**Solution:**
1. Check `backend.log` file
2. Verify environment variables in Secrets
3. Check database file permissions

### Frontend Can't Connect to Backend

**Error:** CORS errors or "Failed to fetch"

**Solution:**
1. Verify backend is running on port 8000
2. Check `backend.log` for errors
3. Make sure URL rewrites are working

---

## 🔧 Customization

### Change Ports

If you need different ports, edit `.replit`:

```ini
[env]
NEXT_PUBLIC_API_URL=""
PORT="8080"  # Change frontend port
```

And `start.sh`:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080  # Change backend port
```

### Add More Environment Variables

Edit `.replit`:
```ini
[env]
NEXT_PUBLIC_API_URL=""
PORT="3000"
YOUR_VAR="your-value"
```

### Use PostgreSQL

Instead of SQLite, connect to external PostgreSQL:

1. Go to Secrets tab
2. Add `DATABASE_URL`:
   ```
   postgresql://user:password@host:5432/database
   ```
3. The app will automatically use PostgreSQL!

---

## 🚀 Deployment

### Deploy to Replit Cloud

1. Click "Deploy" button in sidebar
2. Choose deployment name
3. Click "Deploy"

**That's it!** Your app will be live at:
```
https://your-username.repl.co
```

### Custom Domain (Replit Hacker Plan)

1. Upgrade to Replit Hacker Plan
2. Go to Deploy settings
3. Add custom domain: `app.xseller.ai`
4. Update DNS at your domain provider

---

## 📊 Monitoring

### View Logs

**Backend logs:**
```bash
cat backend.log
tail -f backend.log
```

**Frontend logs:** Shown in Replit console

### Check Processes

```bash
ps aux | grep uvicorn  # Backend
ps aux | grep node     # Frontend
```

### Check Ports

```bash
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
```

---

## ⚡ Performance Tips

### 1. Use Replit's Persistent Storage

Your data persists between sessions:
- SQLite database: `backend/xseller.db`
- Virtual environment: `backend/venv`
- Node modules: `frontend/node_modules`

### 2. Enable Always-On (Paid)

- Keeps your repl running 24/7
- Available in Replit Core/Hacker plans
- Cost: ~$7/month

### 3. Optimize Build

Edit `start.sh` to skip unnecessary steps:

```bash
# Skip npm install if node_modules exists
if [ ! -d "node_modules" ]; then
    npm install
fi
```

---

## 🔒 Security

### Environment Variables

**Never commit secrets!**

Use Replit Secrets for:
- API keys
- Database passwords
- Access tokens

### CORS Configuration

Your backend CORS is configured for production. To adjust:

Edit `.replit` or use Secrets:
```ini
[env]
ALLOWED_ORIGINS="https://yourdomain.com,https://yourdomain2.com"
```

---

## 📝 Checklist

Before deploying:

- [ ] Repl created and imported from GitHub
- [ ] Environment variables added to Secrets
- [ ] Tested locally - "Run" button works
- [ ] Both frontend and backend start successfully
- [ ] Can access app at Replit's URL
- [ ] API calls work (check browser console)
- [ ] No CORS errors
- [ ] Database persists between sessions

---

## 🎉 You're Done!

Your Xseller.ai app is now running on Replit!

**Access it:**
- Development: Replit Webview (after clicking Run)
- Production: https://your-username.repl.co

**Next Steps:**
1. Test all features
2. Configure your domain (if needed)
3. Share your Repl with others
4. Deploy to custom domain (Hacker plan)

---

## 🆘 Need Help?

- **Replit Docs**: https://docs.replit.com
- **Replit Community**: https://replit.com/talk
- **Support**: support@replit.com

---

## 📚 Related Files

- `start.sh` - Startup script
- `.replit` - Replit configuration
- `frontend/next.config.js` - Next.js rewrites
- `frontend/lib/api.ts` - API configuration
- `DEPLOY.md` - Other deployment options

Enjoy deploying! 🚀

