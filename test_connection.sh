#!/bin/bash

echo "🧪 Testing Xseller.ai Backend-Frontend Connection"
echo ""

# Test 1: Backend root endpoint
echo "1️⃣  Testing backend root endpoint..."
if curl -s http://localhost:8000/ | grep -q "Xseller.ai"; then
    echo "   ✅ Backend is running"
else
    echo "   ❌ Backend is NOT running"
    echo "   → Start with: cd backend && uvicorn app.main:app --reload --port 8000"
    exit 1
fi

echo ""

# Test 2: Backend health endpoint
echo "2️⃣  Testing backend health endpoint..."
if curl -s http://localhost:8000/api/health | grep -q "healthy"; then
    echo "   ✅ Health check passed"
else
    echo "   ❌ Health check failed"
fi

echo ""

# Test 3: Dashboard stats endpoint
echo "3️⃣  Testing dashboard stats endpoint..."
STATS=$(curl -s http://localhost:8000/api/stats/dashboard)
if echo "$STATS" | grep -q "queue_stats"; then
    echo "   ✅ Dashboard endpoint working"
    echo "   📊 Response: $STATS" | head -c 100
    echo "..."
else
    echo "   ❌ Dashboard endpoint failed"
fi

echo ""
echo "✨ Test complete!"
echo ""
echo "Next step: Open http://localhost:3000 in your browser"


