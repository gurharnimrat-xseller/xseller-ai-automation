#!/bin/bash

echo "=========================================="
echo "🎤 GENERATING AUDIO SAMPLES FOR COMPARISON"
echo "=========================================="
echo ""

cd /Users/gurvindersinghchadha/Desktop/xseller-ai-automation/backend

# Run the test script
echo "Generating 3 audio samples (professional, energetic, viral)..."
echo ""

source venv/bin/activate
python test_voice_energy.py

echo ""
echo "=========================================="
echo "✅ AUDIO SAMPLES GENERATED!"
echo "=========================================="
echo ""
echo "📂 Audio files location:"
echo "   backend/output/audio/"
echo ""
echo "🎧 To listen:"

# Find the most recent audio files
echo ""
ls -lht backend/output/audio/ | head -4
echo ""

echo "💡 Open these files to hear the difference:"
echo "   1. Professional mode (1.0x speed, stable)"
echo "   2. Energetic mode (1.05x speed, more expressive)"
echo "   3. Viral mode (1.1x speed, high energy)"
echo ""
echo "🔊 Play them side-by-side to compare!"
