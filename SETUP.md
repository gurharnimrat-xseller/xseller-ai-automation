# Xseller.ai Setup Guide

## Issues Fixed

I fixed the following issues preventing frontend-backend connection:

1. ✅ **Router not included**: Added `router` import and `app.include_router(router)` in `main.py`
2. ✅ **CORS middleware order**: Moved CORS middleware BEFORE router inclusion
3. ✅ **API response format mismatch**: Fixed frontend to extract `queue_stats` wrapper from backend response

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (if not exists)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run on: **http://localhost:8000**

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies (if not already done)
npm install

# Start frontend dev server
npm run dev
```

Frontend will run on: **http://localhost:3000**

### 3. Test Connection

Open browser to **http://localhost:3000**

You should see:
- Dashboard loads without errors
- Stats show 0 for all counts (since no data yet)
- No CORS errors in browser console

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

### Frontend can't connect to backend

**Error**: `Failed to fetch` or CORS error in browser console

**Check**:
1. Backend is running on port 8000
2. Backend logs show CORS middleware added
3. Open http://localhost:8000/api/health in browser - should return JSON

**If still failing**, check browser console for exact error message.

### Database errors

**Error**: `Database table not found`

**Solution**: Backend auto-creates tables on startup. Check `xseller.db` exists in `backend/` directory.

## API Endpoints

Once running, test these endpoints:

- GET http://localhost:8000/ → `{"message": "Xseller.ai API", "status": "running"}`
- GET http://localhost:8000/api/health → Health check
- GET http://localhost:8000/api/stats/dashboard → Dashboard stats

## Next Steps

1. Add sample data to test the dashboard
2. Create queue page to view posts
3. Configure publishing providers (Publer, Buffer, etc.)
4. Set up OpenAI API key for content generation

## Environment Variables

Create `.env` file in `backend/` directory:

```env
DATABASE_URL=sqlite:///./xseller.db
OPENAI_API_KEY=your_key_here
PUBLER_API_KEY=your_key_here
```

Copy from `.env.example` if needed.


