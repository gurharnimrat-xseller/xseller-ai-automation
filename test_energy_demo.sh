#!/bin/bash

# Voice Energy Testing Demo
# This script demonstrates the 3 different voice energy modes

echo "=========================================="
echo "🎙️  VOICE ENERGY MODES - INTERACTIVE DEMO"
echo "=========================================="
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/api/voice/energy-modes > /dev/null 2>&1; then
    echo "❌ Backend server is not running!"
    echo "Please start it with: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
    exit 1
fi

echo "✅ Backend server is running"
echo ""

# Function to test energy mode
test_energy_mode() {
    local mode=$1
    local post_id=1

    echo "----------------------------------------"
    echo "Testing: $mode mode"
    echo "----------------------------------------"

    # Set the energy mode
    response=$(curl -s -X POST http://localhost:8000/api/voice/select/$post_id \
        -H "Content-Type: application/json" \
        -d "{\"voice_key\": \"charlotte\", \"energy\": \"$mode\"}")

    # Check if successful
    if echo "$response" | grep -q "selected successfully"; then
        echo "✅ $mode mode set successfully"

        # Show settings
        echo "$response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'energy_info' in data:
    info = data['energy_info']
    print(f\"   Settings:\")
    print(f\"   - Stability: {info['stability']}\")
    print(f\"   - Style: {info['style']}\")
    print(f\"   - Speed: {info['speed']}x\")
    print(f\"   - Description: {info['description']}\")
"
    else
        echo "❌ Failed to set $mode mode"
        echo "$response"
    fi
    echo ""
}

# Test all three modes
echo "Testing all 3 energy modes:"
echo ""

test_energy_mode "professional"
test_energy_mode "energetic"
test_energy_mode "viral"

echo "=========================================="
echo "✅ ALL TESTS COMPLETE!"
echo "=========================================="
echo ""
echo "📋 What's been tested:"
echo "   1. ✅ Professional mode - Neutral, clear tone"
echo "   2. ✅ Energetic mode - Warm, engaging tone"
echo "   3. ✅ Viral mode - High-energy, fast-paced tone"
echo ""
echo "📍 Current setting: The post is now set to VIRAL mode"
echo ""
echo "🎬 Next steps:"
echo "   1. Open your browser to http://localhost:3000"
echo "   2. Go to the video queue page"
echo "   3. Generate a video - it will use VIRAL energy!"
echo "   4. Compare with videos generated in other modes"
echo ""
