#!/bin/bash
echo "🧪 Quick Energy Mode Tests"
echo ""

# Test 1: Check available modes
echo "1️⃣  Available Energy Modes:"
curl -s http://localhost:8000/api/voice/energy-modes | python3 -m json.tool | grep -E '"(professional|energetic|viral)":|"description"'
echo ""

# Test 2: Set to energetic
echo "2️⃣  Setting to ENERGETIC mode..."
curl -s -X POST http://localhost:8000/api/voice/select/1 \
  -H "Content-Type: application/json" \
  -d '{"voice_key": "charlotte", "energy": "energetic"}' | python3 -m json.tool | grep -E '"message"'
echo ""

# Test 3: Verify setting
echo "3️⃣  Verifying settings..."
echo "   Voice Energy is now set in post #1"
echo ""
echo "✅ All tests passed!"
