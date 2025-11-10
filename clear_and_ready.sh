#!/bin/bash

echo "🧹 Clearing all old content from database..."
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "⚠️  Backend server is not running!"
    echo ""
    echo "Please start the backend first:"
    echo "  cd backend"
    echo "  source venv/bin/activate"
    echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    echo ""
    exit 1
fi

# Clear all posts
echo "Deleting all posts and assets..."
RESPONSE=$(curl -s -X DELETE http://localhost:8000/api/content/clear-all)

if echo "$RESPONSE" | grep -q "message"; then
    echo "✅ Successfully cleared all content"
    echo ""
    
    # Verify it's empty
    TOTAL=$(curl -s http://localhost:8000/api/debug/posts | grep -o '"total_posts":[0-9]*' | cut -d: -f2)
    if [ "$TOTAL" = "0" ] || [ -z "$TOTAL" ]; then
        echo "✅ Database is now empty"
        echo ""
        echo "════════════════════════════════════════════════════════════════════"
        echo "🎬 READY FOR FRESH GENERATION"
        echo "════════════════════════════════════════════════════════════════════"
        echo ""
        echo "Next steps:"
        echo "  1. Go to: http://localhost:3000"
        echo "  2. Click '⚡ Generate Demo Content'"
        echo "  3. Wait for the animation (2-3 minutes)"
        echo "  4. Go to Queue tab to see your content"
        echo ""
    else
        echo "⚠️  Warning: $TOTAL posts still remain"
    fi
else
    echo "❌ Error clearing content:"
    echo "$RESPONSE"
    exit 1
fi





