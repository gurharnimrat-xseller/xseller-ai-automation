from __future__ import annotations

"""
Voice Selection System for TTS
Allows users to preview and select voices from ElevenLabs
"""
from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401

import os
from typing import Dict, List, Optional
from pathlib import Path
import httpx


# ==================== CONFIGURATION ====================

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_API_BASE = "https://api.elevenlabs.io/v1"

# Free tier voices on ElevenLabs (Narrator/Neutral style)
RECOMMENDED_VOICES = {
    "adam": {
        "id": "pNInz6obpgDQGcFmaJgB",
        "name": "Adam",
        "gender": "Male",
        "accent": "American",
        "style": "Deep, narrator",
        "use_case": "News, documentaries"
    },
    "antoni": {
        "id": "ErXwobaYiN019PkySvjV",
        "name": "Antoni",
        "gender": "Male",
        "accent": "American",
        "style": "Well-rounded, neutral",
        "use_case": "General narration, news"
    },
    "joseph": {
        "id": "Zlb1dXrM653N07WRdFW3",
        "name": "Joseph",
        "gender": "Male",
        "accent": "British",
        "style": "Professional, news anchor",
        "use_case": "News, professional content"
    },
    "rachel": {
        "id": "21m00Tcm4TlvDq8ikWAM",
        "name": "Rachel",
        "gender": "Female",
        "accent": "American",
        "style": "Professional, calm",
        "use_case": "News, narration"
    },
    "charlotte": {
        "id": "XB0fDUnXU5powFXDhCwa",
        "name": "Charlotte",
        "gender": "Female",
        "accent": "British",
        "style": "Professional, clear",
        "use_case": "News, educational"
    },
    "daniel": {
        "id": "onwK4e9ZLuTAKqWW03F9",
        "name": "Daniel",
        "gender": "Male",
        "accent": "British",
        "style": "Deep, authoritative",
        "use_case": "News, documentaries"
    }
}


# ==================== VOICE ANALYSIS ====================

def analyze_script_style(script: str) -> Dict[str, str]:
    """
    Analyze script to determine the best voice style.

    Returns:
        Dict with style, tone, and recommended characteristics
    """
    script_lower = script.lower()

    # Detect content type
    is_news = any(word in script_lower for word in ['breaking', 'news', 'reported', 'according to', 'announced'])
    is_tech = any(word in script_lower for word in ['ai', 'technology', 'app', 'software', 'tech', 'digital'])
    is_business = any(word in script_lower for word in ['company', 'market', 'business', 'revenue', 'ceo'])

    # Determine style
    if is_news:
        style = "news-anchor"
        tone = "professional, authoritative"
    elif is_tech:
        style = "tech-narrator"
        tone = "clear, engaging"
    elif is_business:
        style = "business-professional"
        tone = "confident, clear"
    else:
        style = "neutral-narrator"
        tone = "balanced, informative"

    # Recommend gender based on content
    # Default to male for news/business, but both work well
    recommended_gender = "male" if (is_news or is_business) else "either"

    # Recommend accent
    # British for more formal/professional, American for tech/casual
    recommended_accent = "British" if is_business else "American/British"

    return {
        "style": style,
        "tone": tone,
        "recommended_gender": recommended_gender,
        "recommended_accent": recommended_accent,
        "is_news": is_news,
        "is_tech": is_tech,
        "is_business": is_business
    }


# ==================== VOICE PREVIEW GENERATION ====================

async def generate_voice_preview(
    voice_id: str,
    voice_name: str,
    sample_text: str,
    output_dir: Optional[str] = None
) -> Optional[str]:
    """
    Generate a preview audio file for a specific voice.

    Args:
        voice_id: ElevenLabs voice ID
        voice_name: Name of the voice (for filename)
        sample_text: Text to synthesize
        output_dir: Optional output directory

    Returns:
        Path to generated preview file or None on failure
    """
    if not ELEVENLABS_API_KEY:
        print(f"[VoiceSelector] Cannot generate preview: ElevenLabs API key not configured")
        return None

    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            }

            url = f"{ELEVENLABS_API_BASE}/text-to-speech/{voice_id}"
            payload = {
                "text": sample_text[:500],  # Limit preview length
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                }
            }

            print(f"[VoiceSelector] Generating preview for {voice_name}...")
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)

            if response.status_code == 200:
                # Save preview audio
                if not output_dir:
                    output_dir = Path(__file__).parent.parent / "output" / "voice_previews"
                else:
                    output_dir = Path(output_dir)

                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / f"preview_{voice_name.lower()}.mp3"

                with open(output_path, "wb") as f:
                    f.write(response.content)

                print(f"[VoiceSelector] ✅ Preview generated: {output_path}")
                return str(output_path)
            else:
                print(f"[VoiceSelector] API error for {voice_name}: {response.status_code}")
                return None

    except Exception as e:
        print(f"[VoiceSelector] Error generating preview for {voice_name}: {e}")
        return None


async def generate_all_previews(
    script: str,
    recommended_only: bool = True
) -> Dict[str, str]:
    """
    Generate preview audio files for all recommended voices.

    Args:
        script: Script to analyze and use for preview
        recommended_only: If True, only generate previews for recommended voices

    Returns:
        Dict mapping voice names to preview file paths
    """
    # Analyze script
    style_analysis = analyze_script_style(script)

    print(f"\n{'='*80}")
    print(f"📊 SCRIPT ANALYSIS")
    print(f"{'='*80}")
    print(f"Style: {style_analysis['style']}")
    print(f"Tone: {style_analysis['tone']}")
    print(f"Recommended Gender: {style_analysis['recommended_gender']}")
    print(f"Recommended Accent: {style_analysis['recommended_accent']}")
    print(f"{'='*80}\n")

    # Extract sample text (first 100 words or so)
    words = script.split()[:100]
    sample_text = " ".join(words)

    # Generate previews
    previews = {}

    # Filter voices based on analysis if recommended_only
    voices_to_preview = RECOMMENDED_VOICES.copy()

    if recommended_only:
        # Filter by gender preference
        if style_analysis['recommended_gender'] == 'male':
            voices_to_preview = {k: v for k, v in voices_to_preview.items() if v['gender'] == 'Male'}
        elif style_analysis['recommended_gender'] == 'female':
            voices_to_preview = {k: v for k, v in voices_to_preview.items() if v['gender'] == 'Female'}

    print(f"🎙️ Generating {len(voices_to_preview)} voice previews...\n")

    for voice_key, voice_info in voices_to_preview.items():
        preview_path = await generate_voice_preview(
            voice_id=voice_info['id'],
            voice_name=voice_info['name'],
            sample_text=sample_text
        )

        if preview_path:
            previews[voice_key] = preview_path

    return previews


# ==================== VOICE SELECTION ====================

def get_voice_recommendations(script: str) -> List[Dict]:
    """
    Get recommended voices based on script analysis.

    Returns:
        List of recommended voice configs sorted by relevance
    """
    style_analysis = analyze_script_style(script)

    recommendations = []

    for voice_key, voice_info in RECOMMENDED_VOICES.items():
        score = 0
        reasons = []

        # Gender match
        if style_analysis['recommended_gender'] == 'either':
            score += 5
        elif style_analysis['recommended_gender'].lower() == voice_info['gender'].lower():
            score += 10
            reasons.append(f"Matches recommended gender ({voice_info['gender']})")

        # Accent match
        if voice_info['accent'] in style_analysis['recommended_accent']:
            score += 8
            reasons.append(f"Matches recommended accent ({voice_info['accent']})")

        # Style/use case match
        if style_analysis['is_news'] and 'news' in voice_info['use_case'].lower():
            score += 10
            reasons.append("Perfect for news content")

        if style_analysis['is_tech'] and any(word in voice_info['style'].lower() for word in ['clear', 'engaging']):
            score += 8
            reasons.append("Great for tech content")

        if style_analysis['is_business'] and 'professional' in voice_info['style'].lower():
            score += 10
            reasons.append("Professional tone for business")

        recommendations.append({
            **voice_info,
            "key": voice_key,
            "score": score,
            "reasons": reasons
        })

    # Sort by score (highest first)
    recommendations.sort(key=lambda x: x['score'], reverse=True)

    return recommendations


def display_recommendations(recommendations: List[Dict]) -> None:
    """Display voice recommendations to console."""
    print(f"\n{'='*80}")
    print(f"🎤 RECOMMENDED VOICES (Top to Bottom)")
    print(f"{'='*80}\n")

    for i, voice in enumerate(recommendations[:6], 1):
        print(f"{i}. {voice['name']} ({voice['gender']}, {voice['accent']})")
        print(f"   Style: {voice['style']}")
        print(f"   Best for: {voice['use_case']}")
        print(f"   Score: {voice['score']}/30")
        if voice['reasons']:
            print(f"   Why: {', '.join(voice['reasons'])}")
        print()


# ==================== TESTING ====================

async def test_voice_selector(script: str):
    """Test the voice selector with a sample script."""
    print(f"\n{'='*80}")
    print(f"🎬 VOICE SELECTOR TEST")
    print(f"{'='*80}\n")

    # Get recommendations
    recommendations = get_voice_recommendations(script)
    display_recommendations(recommendations)

    # Generate previews for top 3
    print(f"\n{'='*80}")
    print(f"🎙️ GENERATING PREVIEW AUDIO (Top 3 Voices)")
    print(f"{'='*80}\n")

    top_3 = recommendations[:3]
    previews = {}

    for voice in top_3:
        preview_path = await generate_voice_preview(
            voice_id=voice['id'],
            voice_name=voice['name'],
            sample_text=script[:200]
        )
        if preview_path:
            previews[voice['key']] = preview_path

    print(f"\n{'='*80}")
    print(f"✅ PREVIEW GENERATION COMPLETE")
    print(f"{'='*80}")
    print(f"\nGenerated {len(previews)} preview files:")
    for voice_key, path in previews.items():
        voice_name = RECOMMENDED_VOICES[voice_key]['name']
        print(f"  • {voice_name}: {path}")
    print()

    return previews


if __name__ == "__main__":
    import asyncio

    # Test with a sample news script
    test_script = """
    Breaking News: OpenAI has just announced a major update to their AI technology.
    According to the company, this new development will revolutionize how we interact
    with artificial intelligence. The CEO stated that this represents a significant
    milestone in the tech industry.
    """

    asyncio.run(test_voice_selector(test_script))
