"""
Test voice energy modes (professional vs energetic vs viral)
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import tts_service


async def main():
    print("="*80)
    print("🎙️  TESTING VOICE ENERGY MODES")
    print("="*80)

    # Test script
    test_text = "CRED is revolutionizing customer experience in India with OpenAI. GPT-powered tools analyze queries instantly and provide personalized responses."

    print(f"\n📝 Test Text: {test_text[:100]}...\n")

    # Test each energy mode
    energy_modes = ["professional", "energetic", "viral"]

    for energy in energy_modes:
        print(f"\n{'='*80}")
        print(f"🔊 Testing Energy Mode: {energy.upper()}")
        print(f"{'='*80}")

        energy_preset = tts_service.VOICE_ENERGY_PRESETS[energy]
        print(f"   Description: {energy_preset['description']}")
        print(f"   Settings:")
        print(f"   - Stability: {energy_preset['stability']}")
        print(f"   - Style: {energy_preset['style']}")
        print(f"   - Speed: {energy_preset['speed']}x")
        print(f"\n   Generating audio...")

        # Generate audio
        audio_path = await tts_service.generate_voiceover(
            text=test_text,
            provider="auto",  # Will try ElevenLabs -> OpenAI -> gTTS
            voice="charlotte",
            energy=energy
        )

        if audio_path:
            file_size = os.path.getsize(audio_path) / 1024  # KB
            print(f"   ✅ Audio generated: {audio_path}")
            print(f"   📦 File size: {file_size:.2f} KB")
        else:
            print(f"   ❌ Audio generation failed")

    print("\n" + "="*80)
    print("✅ VOICE ENERGY TESTING COMPLETE!")
    print("="*80)
    print("\n📍 Audio files are saved in: backend/output/audio/")
    print("💡 Listen to each file to compare the energy levels")


if __name__ == "__main__":
    asyncio.run(main())
