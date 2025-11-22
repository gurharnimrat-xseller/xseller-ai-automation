"""
Enhanced Text-to-Speech (TTS) Service
Supports multiple TTS providers with automatic fallback:
- ElevenLabs (premium quality)
- OpenAI TTS (high quality, cost-effective)
- gTTS (free fallback)
"""
from __future__ import annotations

# from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Literal
import httpx

# Import gTTS if available
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# Import OpenAI if available
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# ==================== CONFIGURATION ====================

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ELEVENLABS_API_BASE = "https://api.elevenlabs.io/v1"

# Voice configurations
ELEVENLABS_VOICES = {
    "rachel": "21m00Tcm4TlvDq8ikWAM",  # Female, professional
    "adam": "pNInz6obpgDQGcFmaJgB",    # Male, deep
    "bella": "EXAVITQu4vr4xnSDxMaL",   # Female, soft
    "antoni": "ErXwobaYiN019PkySvjV",  # Male, well-rounded
    "charlotte": "XB0fDUnXU5powFXDhCwa",  # British female, professional
    "charlie": "IKne3meq5aSn9XLyUdCD",    # British male, energetic
}

OPENAI_VOICES = {
    "alloy": "alloy",      # Neutral
    "echo": "echo",        # Male, professional
    "fable": "fable",      # British male, expressive
    "onyx": "onyx",        # Deep male
    "nova": "nova",        # Female, warm
    "shimmer": "shimmer",  # Soft female
}

# Default voice selections (British professional voices)
DEFAULT_ELEVENLABS_VOICE = "charlotte"  # British female, professional
DEFAULT_OPENAI_VOICE = "fable"          # British male, expressive

# TTS provider priority (will try in order)
TTS_PROVIDER_PRIORITY = ["elevenlabs", "openai", "gtts"]

# Voice energy/tone presets
VOICE_ENERGY_PRESETS = {
    "professional": {
        "stability": 0.5,           # Balanced, consistent delivery
        "similarity_boost": 0.75,   # High clarity
        "style": 0.0,               # Minimal style variation
        "use_speaker_boost": True,
        "speed": 1.0,               # Normal speed
        "description": "Neutral, clear, professional tone"
    },
    "energetic": {
        "stability": 0.3,           # More variation for energy
        "similarity_boost": 0.85,   # Higher engagement
        "style": 0.5,               # More expressive
        "use_speaker_boost": True,
        "speed": 1.05,              # Slightly faster for energy
        "description": "Warm, engaging, enthusiastic tone"
    },
    "viral": {
        "stability": 0.2,           # Maximum variation
        "similarity_boost": 0.9,    # Maximum engagement
        "style": 0.7,               # Very expressive
        "use_speaker_boost": True,
        "speed": 1.1,               # Faster pacing
        "description": "High-energy, personality-driven, viral-ready"
    }
}

DEFAULT_ENERGY = "professional"


# ==================== TTS PROVIDER FUNCTIONS ====================

async def generate_tts_elevenlabs(
    text: str,
    voice: str = DEFAULT_ELEVENLABS_VOICE,
    output_path: Optional[str] = None,
    energy: str = DEFAULT_ENERGY
) -> Optional[str]:
    """
    Generate TTS using ElevenLabs API (premium quality).

    Args:
        text: Text to convert to speech
        voice: Voice name (rachel, adam, bella, antoni)
        output_path: Optional output file path

    Returns:
        Path to generated audio file or None on failure
    """
    if not ELEVENLABS_API_KEY:
        print("[TTS] ElevenLabs API key not configured")
        return None

    try:
        # Get voice ID
        voice_id = ELEVENLABS_VOICES.get(voice.lower(), ELEVENLABS_VOICES[DEFAULT_ELEVENLABS_VOICE])

        # Get energy preset
        energy_preset = VOICE_ENERGY_PRESETS.get(energy.lower(), VOICE_ENERGY_PRESETS[DEFAULT_ENERGY])

        async with httpx.AsyncClient() as client:
            headers = {
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            }

            url = f"{ELEVENLABS_API_BASE}/text-to-speech/{voice_id}"
            payload = {
                "text": text[:5000],  # Limit to 5000 chars
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": energy_preset["stability"],
                    "similarity_boost": energy_preset["similarity_boost"],
                    "style": energy_preset["style"],
                    "use_speaker_boost": energy_preset["use_speaker_boost"]
                }
            }

            print(f"[TTS] Generating ElevenLabs TTS with voice: {voice}, energy: {energy} ({energy_preset['description']})")
            response = await client.post(url, headers=headers, json=payload, timeout=60.0)

            if response.status_code == 200:
                # Save audio file
                if not output_path:
                    audio_dir = Path(__file__).parent.parent / "output" / "audio"
                    audio_dir.mkdir(parents=True, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_path = str(audio_dir / f"elevenlabs_{timestamp}.mp3")

                with open(output_path, "wb") as f:
                    f.write(response.content)

                print(f"[TTS] ✅ ElevenLabs TTS generated: {output_path}")
                return output_path
            else:
                print(f"[TTS] ElevenLabs API error: {response.status_code} - {response.text}")
                return None

    except Exception as e:
        print(f"[TTS] ElevenLabs error: {e}")
        return None


async def generate_tts_openai(
    text: str,
    voice: str = DEFAULT_OPENAI_VOICE,
    output_path: Optional[str] = None,
    energy: str = DEFAULT_ENERGY
) -> Optional[str]:
    """
    Generate TTS using OpenAI API (high quality, cost-effective).

    Args:
        text: Text to convert to speech
        voice: Voice name (alloy, echo, fable, onyx, nova, shimmer)
        output_path: Optional output file path
        energy: Energy mode (professional, energetic, viral)

    Returns:
        Path to generated audio file or None on failure
    """
    if not OPENAI_AVAILABLE or not OPENAI_API_KEY:
        print("[TTS] OpenAI not available or API key not configured")
        return None

    try:
        # Get voice name
        voice_name = OPENAI_VOICES.get(voice.lower(), DEFAULT_OPENAI_VOICE)

        # Get energy preset for speed adjustment
        energy_preset = VOICE_ENERGY_PRESETS.get(energy.lower(), VOICE_ENERGY_PRESETS[DEFAULT_ENERGY])

        # Initialize OpenAI client
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)

        print(f"[TTS] Generating OpenAI TTS with voice: {voice_name}, energy: {energy} ({energy_preset['description']})")
        response = await client.audio.speech.create(
            model="tts-1-hd",  # Higher quality model for more natural sound
            voice=voice_name,
            input=text[:4096],  # OpenAI limit
            speed=energy_preset["speed"]  # Adjust speed based on energy mode
        )

        # Save audio file
        if not output_path:
            audio_dir = Path(__file__).parent.parent / "output" / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(audio_dir / f"openai_{timestamp}.mp3")

        # Write audio content
        with open(output_path, "wb") as f:
            f.write(response.content)

        print(f"[TTS] ✅ OpenAI TTS generated: {output_path}")
        return output_path

    except Exception as e:
        print(f"[TTS] OpenAI error: {e}")
        return None


async def generate_tts_gtts(
    text: str,
    lang: str = "en",
    tld: str = "co.uk",  # British accent
    output_path: Optional[str] = None
) -> Optional[str]:
    """
    Generate TTS using gTTS (free, basic quality fallback).

    Args:
        text: Text to convert to speech
        lang: Language code (default: en)
        tld: Top-level domain for accent (co.uk for British)
        output_path: Optional output file path

    Returns:
        Path to generated audio file or None on failure
    """
    if not GTTS_AVAILABLE:
        print("[TTS] gTTS not available")
        return None

    try:
        print("[TTS] Generating gTTS with British accent (free fallback)")

        # Create TTS with British accent
        tts = gTTS(text=text[:5000], lang=lang, tld=tld, slow=False)

        # Save audio file
        if not output_path:
            audio_dir = Path(__file__).parent.parent / "output" / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(audio_dir / f"gtts_{timestamp}.mp3")

        tts.save(output_path)

        print(f"[TTS] ✅ gTTS generated: {output_path}")
        return output_path

    except Exception as e:
        print(f"[TTS] gTTS error: {e}")
        return None


# ==================== MAIN TTS INTERFACE ====================

async def generate_voiceover(
    text: str,
    provider: Optional[Literal["elevenlabs", "openai", "gtts", "auto"]] = "auto",
    voice: Optional[str] = None,
    output_path: Optional[str] = None,
    energy: str = DEFAULT_ENERGY
) -> Optional[str]:
    """
    Generate voiceover with automatic provider fallback.

    Args:
        text: Text to convert to speech
        provider: TTS provider to use ("elevenlabs", "openai", "gtts", "auto")
        voice: Voice name (provider-specific)
        output_path: Optional output file path
        energy: Energy mode - "professional" (neutral, clear), "energetic" (warm, engaging), "viral" (high-energy)

    Returns:
        Path to generated audio file or None on failure

    Example:
        # Auto-select best available provider with professional tone
        audio_path = await generate_voiceover("Hello world!")

        # Use energetic delivery for viral content
        audio_path = await generate_voiceover("Hello world!", energy="energetic")

        # Use specific provider with viral energy
        audio_path = await generate_voiceover("Hello world!", provider="elevenlabs", voice="charlotte", energy="viral")
    """
    if not text or not text.strip():
        print("[TTS] No text provided")
        return None

    # Clean text
    text = text.strip()

    # Auto-select provider
    if provider == "auto":
        providers_to_try = TTS_PROVIDER_PRIORITY
    else:
        providers_to_try = [provider]

    # Try each provider in order
    for provider_name in providers_to_try:
        print(f"[TTS] Trying provider: {provider_name}")

        try:
            if provider_name == "elevenlabs":
                result = await generate_tts_elevenlabs(
                    text=text,
                    voice=voice or DEFAULT_ELEVENLABS_VOICE,
                    output_path=output_path,
                    energy=energy
                )
                if result:
                    return result

            elif provider_name == "openai":
                result = await generate_tts_openai(
                    text=text,
                    voice=voice or DEFAULT_OPENAI_VOICE,
                    output_path=output_path,
                    energy=energy
                )
                if result:
                    return result

            elif provider_name == "gtts":
                result = await generate_tts_gtts(
                    text=text,
                    output_path=output_path
                )
                if result:
                    return result

        except Exception as e:
            print(f"[TTS] Error with {provider_name}: {e}")
            continue

    print("[TTS] ❌ All TTS providers failed")
    return None


# ==================== UTILITY FUNCTIONS ====================

def get_available_providers() -> list[str]:
    """Get list of available TTS providers."""
    providers = []

    if ELEVENLABS_API_KEY:
        providers.append("elevenlabs")
    if OPENAI_AVAILABLE and OPENAI_API_KEY:
        providers.append("openai")
    if GTTS_AVAILABLE:
        providers.append("gtts")

    return providers


def get_available_voices(provider: str) -> list[str]:
    """Get list of available voices for a provider."""
    if provider == "elevenlabs":
        return list(ELEVENLABS_VOICES.keys())
    elif provider == "openai":
        return list(OPENAI_VOICES.keys())
    elif provider == "gtts":
        return ["default"]
    else:
        return []


# ==================== TESTING ====================

async def test_tts():
    """Test TTS generation with all available providers."""
    test_text = "Hello! This is a test of the text to speech system. How does it sound?"

    print("\n" + "="*80)
    print("🎤 TESTING TTS PROVIDERS")
    print("="*80 + "\n")

    providers = get_available_providers()
    print(f"Available providers: {', '.join(providers)}\n")

    # Test auto-selection
    print("Testing auto-selection...")
    result = await generate_voiceover(test_text, provider="auto")
    if result:
        print(f"✅ Auto-selection successful: {result}")
    else:
        print("❌ Auto-selection failed")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_tts())
