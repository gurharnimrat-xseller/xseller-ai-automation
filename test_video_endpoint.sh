#!/bin/bash

echo "🎬 Testing Video Generation Endpoint"
echo ""

# Step 1: Generate demo data
echo "Step 1: Generating demo posts..."
GENERATE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/content/generate-demo)
echo "Response: $GENERATE_RESPONSE"
echo ""

# Step 2: Get first post ID
echo "Step 2: Finding available post ID..."
POST_ID=$(curl -s "http://localhost:8000/api/content/queue?limit=1" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)

if [ -z "$POST_ID" ]; then
    echo "❌ No posts found. Trying with ID 1..."
    POST_ID=1
else
    echo "✅ Found post ID: $POST_ID"
fi
echo ""

# Step 3: Test the video endpoint
echo "Step 3: Testing video generation endpoint with post ID $POST_ID..."
echo "Endpoint: POST http://localhost:8000/api/video/competitor-test/$POST_ID"
echo ""

RESPONSE=$(curl -s -X POST "http://localhost:8000/api/video/competitor-test/$POST_ID")
echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

if echo "$RESPONSE" | grep -q "success"; then
    echo "✅ Video generation successful!"
    VIDEO_PATH=$(echo "$RESPONSE" | grep -o '"video_path":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$VIDEO_PATH" ]; then
        echo "Video saved at: $VIDEO_PATH"
    fi
elif echo "$RESPONSE" | grep -q "Post not found"; then
    echo "❌ Post ID $POST_ID not found. Try generating demo data first."
    echo "   Run: curl -X POST http://localhost:8000/api/content/generate-demo"
else
    echo "⚠️  Check the response above for details."
fi





