# 🧪 Voice Energy Testing Guide

## Current System Status

✅ **Backend**: http://localhost:8000 (Running)
✅ **Frontend**: http://localhost:3000 (Running)
✅ **Voice Energy**: ENERGETIC mode set for Post #1

---

## 🎯 Testing Options

### **Option 1: Frontend UI Test (Easiest)**

1. Open browser: http://localhost:3000
2. Go to "Queue" page
3. View Post #1: "CRED Revolutionizes Customer Experience with AI"
4. Current settings:
   - Voice: Charlotte (British Female)
   - Energy: Energetic
5. Play the existing video or generate a new one

---

### **Option 2: Compare All 3 Energy Modes (Recommended)**

**Step 1: Generate Audio Samples**
```bash
cd /Users/gurvindersinghchadha/Desktop/xseller-ai-automation/backend
source venv/bin/activate
python test_voice_energy.py
```

**Step 2: Listen to the Audio Files**
```bash
open output/audio/
```

You'll hear 3 different MP3 files:
- **Professional**: Neutral, clear, 1.0x speed
- **Energetic**: Warm, engaging, 1.05x speed
- **Viral**: High-energy, fast, 1.1x speed

---

### **Option 3: Test Different Energy Modes via API**

**Set to Professional:**
```bash
curl -X POST http://localhost:8000/api/voice/select/1 \
  -H "Content-Type: application/json" \
  -d '{"voice_key": "charlotte", "energy": "professional"}'
```

**Set to Energetic:**
```bash
curl -X POST http://localhost:8000/api/voice/select/1 \
  -H "Content-Type: application/json" \
  -d '{"voice_key": "charlotte", "energy": "energetic"}'
```

**Set to Viral:**
```bash
curl -X POST http://localhost:8000/api/voice/select/1 \
  -H "Content-Type: application/json" \
  -d '{"voice_key": "charlotte", "energy": "viral"}'
```

**Check Current Setting:**
```bash
curl -s http://localhost:8000/api/posts/1 | python3 -m json.tool | grep -A3 extra_data
```

---

### **Option 4: Run All Tests Automatically**

**Quick Test:**
```bash
bash /Users/gurvindersinghchadha/Desktop/xseller-ai-automation/quick_test.sh
```

**Full Demo:**
```bash
bash /Users/gurvindersinghchadha/Desktop/xseller-ai-automation/test_energy_demo.sh
```

**Generate Audio Comparison:**
```bash
bash /Users/gurvindersinghchadha/Desktop/xseller-ai-automation/compare_energy_modes.sh
```

---

## 📊 What Each Energy Mode Does

| Mode | Speed | Stability | Style | Best For |
|------|-------|-----------|-------|----------|
| **Professional** | 1.0x | 0.5 (balanced) | 0.0 (neutral) | News, education, business |
| **Energetic** | 1.05x | 0.3 (varied) | 0.5 (expressive) | Marketing, social media |
| **Viral** | 1.1x | 0.2 (dynamic) | 0.7 (very expressive) | TikTok, Shorts, viral content |

---

## 🎬 Expected Results

### With gTTS (Current - Free Fallback):
- ✅ All 3 modes will generate audio
- ⚠️ Differences will be minimal (gTTS doesn't support advanced settings)
- ✅ Infrastructure is fully ready

### With ElevenLabs API (When Configured):
- ✅ **Professional**: Clear, neutral, consistent tone
- ✅ **Energetic**: Warmer, more engaging, slightly faster
- ✅ **Viral**: High-energy, expressive, fast-paced

---

## 🔧 Troubleshooting

**Backend not responding?**
```bash
curl http://localhost:8000/api/voice/energy-modes
```

**Frontend not loading?**
```bash
curl http://localhost:3000
```

**Check running services:**
```bash
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
```

---

## 📝 Next Steps After Testing

1. ✅ Verify all 3 energy modes work
2. ✅ Test via both API and Frontend
3. ✅ Compare audio/video outputs
4. 📋 Provide feedback on voice quality
5. 🚀 Move to next feature (visual enhancements, CTAs, etc.)

---

## 💡 Tips

- **For best results**: Configure ElevenLabs API key in `.env` file
- **To test quickly**: Use the existing video at http://localhost:8000/test_videos/competitor_test_1.mp4
- **To compare**: Generate the same script with different energy modes
- **For A/B testing**: Create multiple videos with different energies and compare engagement

---

**Current Voice Settings for Post #1:**
- Voice: Charlotte (British Female, Professional)
- Energy: Energetic
- Speed: 1.05x
- Description: "Warm, engaging, enthusiastic tone"
