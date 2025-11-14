"""
Competitor-Style Video Production (Tech Focus, Clean)
Replicates viral YouTube Shorts/TikTok tech videos with:
- Word-by-word text animations
- Bold typography
- Fast-paced editing
- Clean tech aesthetic
- Professional transitions
"""

from __future__ import annotations

import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Video generation imports
try:
    from moviepy.editor import (
        VideoFileClip, ColorClip, TextClip, CompositeVideoClip,  # noqa: F401
        concatenate_videoclips, AudioFileClip, ImageClip
    )
    from moviepy.video.fx.all import fadein, fadeout, resize  # noqa: F401
    from moviepy.video.fx.all import crop  # noqa: F401
    import numpy as np
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

import httpx
from PIL import Image, ImageDraw, ImageFont

# Video settings (9:16 vertical for shorts) - defined early for function defaults
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

# ==================== PIL-BASED TEXT RENDERING (NO IMAGEMAGICK) ====================

def create_text_image_pil(
    text: str,
    fontsize: int,
    color: str = "white",
    stroke_color: str = "black",
    stroke_width: int = 3,
    bg_color: Optional[str] = None,
    size: Tuple[int, int] = (VIDEO_WIDTH, VIDEO_HEIGHT),
) -> Image.Image:
    """
    Create text image using PIL (no ImageMagick required).
    Returns a PIL Image that can be converted to ImageClip.
    """
    # Create image
    img = Image.new('RGBA', size, (0, 0, 0, 0) if not bg_color else bg_color)
    draw = ImageDraw.Draw(img)

    # Try to load a bold font, fallback to default
    try:
        # Try common bold font paths
        font_paths = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
        font = None
        for path in font_paths:
            if os.path.exists(path):
                font = ImageFont.truetype(path, fontsize)
                break
        if not font:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center text
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    # Draw text with stroke (outline)
    if stroke_width > 0:
        # Draw outline
        for adj_x in range(-stroke_width, stroke_width + 1):
            for adj_y in range(-stroke_width, stroke_width + 1):
                draw.text((x + adj_x, y + adj_y), text, font=font, fill=stroke_color)

    # Draw main text
    draw.text((x, y), text, font=font, fill=color)

    return img


# ==================== CONFIGURATION ====================

# API Keys
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# Video settings (9:16 vertical for shorts) - VIDEO_WIDTH and VIDEO_HEIGHT defined above
VIDEO_FPS = 30

# Competitor-style text settings
TEXT_FONT_BOLD = "Arial-Bold"
TEXT_FONT_BLACK = "Impact"
TEXT_SIZE_LARGE = 120  # Extra large for main text
TEXT_SIZE_MEDIUM = 90
TEXT_SIZE_SMALL = 70

# Tech-focused color palette
COLORS = {
    "tech_blue": "#0066FF",
    "tech_cyan": "#00D9FF",
    "tech_purple": "#6B46FF",
    "tech_green": "#00FF88",
    "dark_bg": "#0A0E1A",
    "light_bg": "#1A1F35",
    "white": "#FFFFFF",
    "yellow_highlight": "#FFD700",
}


# ==================== SCRIPT PARSING ====================

def parse_script_competitor_style(script: str) -> List[Dict[str, Any]]:
    """
    Parse script into rapid-fire scenes (1-3 seconds each).
    Splits text into short, punchy segments.
    """
    scenes = []

    # First try to parse with timing
    pattern = r'(Hook|Main|Why|CTA)\s*\((\d+)-(\d+)s?\):\s*(.+?)(?=(?:Hook|Main|Why|CTA)\s*\(|\Z)'
    matches = list(re.finditer(pattern, script, re.IGNORECASE | re.DOTALL))

    if matches:
        for match in matches:
            scene_type = match.group(1).lower()
            start_time = int(match.group(2))
            end_time = int(match.group(3))
            text = match.group(4).strip()

            # Split into shorter segments (max 10 words per scene)
            sentences = re.split(r'[.!?]\s+|\n+', text)
            segment_duration = (end_time - start_time) / max(len(sentences), 1)

            cumulative = start_time
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue

                # Further split long sentences into chunks
                words = sentence.split()
                if len(words) > 10:
                    # Split into 10-word chunks
                    for i in range(0, len(words), 10):
                        chunk = ' '.join(words[i:i+10])
                        scenes.append({
                            "type": scene_type,
                            "text": chunk,
                            "start_time": cumulative,
                            "duration": min(3, segment_duration),
                            "words": chunk.split(),
                        })
                        cumulative += min(3, segment_duration)
                else:
                    scenes.append({
                        "type": scene_type,
                        "text": sentence,
                        "start_time": cumulative,
                        "duration": min(3, segment_duration),
                        "words": sentence.split(),
                    })
                    cumulative += min(3, segment_duration)
    else:
        # Fallback: split by sentences
        sentences = re.split(r'[.!?]\s+|\n+', script)
        cumulative = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            duration = max(2, min(len(sentence.split()) * 0.3, 4))
            scenes.append({
                "type": "main",
                "text": sentence,
                "start_time": cumulative,
                "duration": duration,
                "words": sentence.split(),
            })
            cumulative += duration

    # Set end times
    for scene in scenes:
        scene["end_time"] = scene["start_time"] + scene["duration"]

    print(f"[video_pro] Parsed {len(scenes)} rapid-fire scenes")
    return scenes


# ==================== ADVANCED TEXT ANIMATIONS ====================

def create_word_by_word_clip(
    words: List[str],
    duration: float,
    size: Tuple[int, int] = (VIDEO_WIDTH, VIDEO_HEIGHT),
    fontsize: int = TEXT_SIZE_LARGE,
    color: str = COLORS["white"],
    bg_color: str = COLORS["dark_bg"],
    highlight_color: str = COLORS["yellow_highlight"],
) -> CompositeVideoClip:
    """
    Create competitor-style word-by-word animation.
    Each word pops in with emphasis.
    """
    if not MOVIEPY_AVAILABLE:
        raise ImportError("MoviePy not available")

    # Background
    bg = ColorClip(size=size, color=bg_color, duration=duration)

    # Calculate timing for each word
    time_per_word = duration / len(words)

    text_clips = []

    for i, word in enumerate(words):
        # Word appears at this time
        start_time = i * time_per_word
        word_duration = duration - start_time

        # Create text clip with emphasis
        # Make current word larger/highlighted
        word_fontsize = fontsize if i < len(words) - 1 else int(fontsize * 1.2)
        word_color = color if i < len(words) - 1 else highlight_color

        try:
            # Use PIL to create text image (no ImageMagick needed)
            text_img = create_text_image_pil(
                word,
                fontsize=word_fontsize,
                color=word_color,
                stroke_color="black",
                stroke_width=4,
                size=size
            )

            # Convert PIL image to MoviePy ImageClip
            txt = ImageClip(np.array(text_img)).set_duration(word_duration)

            # Position words flowing down the screen
            y_position = 'center' if len(words) <= 3 else 400 + (i * 150)

            txt = txt.set_position(('center', y_position))
            txt = txt.set_start(start_time)

            # Add pop-in animation (scale effect)
            txt = txt.crossfadein(0.1)

            text_clips.append(txt)
        except Exception as e:
            print(f"[video_pro] Warning: Could not create text for '{word}': {e}")
            continue

    # Composite all elements
    if text_clips:
        final = CompositeVideoClip([bg] + text_clips, size=size)
    else:
        final = bg

    return final


def create_bold_text_clip(
    text: str,
    duration: float,
    size: Tuple[int, int] = (VIDEO_WIDTH, VIDEO_HEIGHT),
    fontsize: int = TEXT_SIZE_LARGE,
    color: str = COLORS["white"],
    bg_color: str = COLORS["dark_bg"],
    animation_style: str = "fade"
) -> CompositeVideoClip:
    """
    Create bold, centered text with clean animation.
    """
    if not MOVIEPY_AVAILABLE:
        raise ImportError("MoviePy not available")

    # Background
    bg = ColorClip(size=size, color=bg_color, duration=duration)

    # Split text into lines if too long
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        if len(' '.join(current_line)) > 20:
            if len(current_line) > 1:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(' '.join(current_line))
                current_line = []

    if current_line:
        lines.append(' '.join(current_line))

    formatted_text = '\n'.join(lines)

    try:
        # Create main text using PIL (no ImageMagick needed)
        text_img = create_text_image_pil(
            formatted_text,
            fontsize=fontsize,
            color=color,
            stroke_color="black",
            stroke_width=4,
            size=size
        )

        # Convert PIL image to MoviePy ImageClip
        txt = ImageClip(np.array(text_img)).set_duration(duration)
        txt = txt.set_position('center')
        txt = txt.set_duration(duration)

        # Apply animation
        if animation_style == "fade":
            txt = txt.crossfadein(0.2).crossfadeout(0.2)
        elif animation_style == "slide":
            txt = txt.set_position(lambda t: ('center', min(960, -200 + t * 400)))

        final = CompositeVideoClip([bg, txt], size=size)
    except Exception as e:
        print(f"[video_pro] Error creating text clip: {e}")
        final = bg

    return final


# ==================== SCENE GENERATION ====================

async def create_competitor_scene(
    scene: Dict[str, Any],
    output_size: Tuple[int, int] = (VIDEO_WIDTH, VIDEO_HEIGHT),
    use_word_by_word: bool = True
) -> CompositeVideoClip:
    """
    Create scene in competitor style (tech focus, clean).
    """
    if not MOVIEPY_AVAILABLE:
        raise ImportError("MoviePy not available")

    duration = scene.get("duration", 3.0)
    text = scene.get("text", "")
    words = scene.get("words", text.split())
    scene_type = scene.get("type", "main")

    print(f"[video_pro] Creating scene: {scene_type} ({duration}s) - {text[:50]}...")

    # Choose color scheme based on scene type
    color_schemes = {
        "hook": {"bg": COLORS["dark_bg"], "text": COLORS["yellow_highlight"]},
        "main": {"bg": COLORS["tech_blue"], "text": COLORS["white"]},
        "why": {"bg": COLORS["tech_purple"], "text": COLORS["white"]},
        "cta": {"bg": COLORS["tech_green"], "text": COLORS["dark_bg"]},
    }

    scheme = color_schemes.get(scene_type, {"bg": COLORS["dark_bg"], "text": COLORS["white"]})

    # Create scene with word-by-word animation for short text
    if use_word_by_word and len(words) <= 8 and duration <= 4:
        scene_clip = create_word_by_word_clip(
            words=words,
            duration=duration,
            size=output_size,
            fontsize=TEXT_SIZE_LARGE,
            color=scheme["text"],
            bg_color=scheme["bg"],
        )
    else:
        # Use bold centered text for longer content
        scene_clip = create_bold_text_clip(
            text=text,
            duration=duration,
            size=output_size,
            fontsize=TEXT_SIZE_MEDIUM,
            color=scheme["text"],
            bg_color=scheme["bg"],
            animation_style="fade"
        )

    return scene_clip


# ==================== VOICEOVER (from original) ====================

async def generate_voiceover_elevenlabs(text: str) -> Optional[str]:
    """Generate voiceover using Eleven Labs."""
    if not ELEVENLABS_API_KEY:
        return None

    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            }

            voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                }
            }

            response = await client.post(url, headers=headers, json=payload, timeout=60.0)

            if response.status_code == 200:
                audio_dir = Path(__file__).parent.parent / "output" / "audio"
                audio_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = str(audio_dir / f"voiceover_{timestamp}.mp3")

                with open(output_path, "wb") as f:
                    f.write(response.content)

                print(f"[video_pro] ✅ Voiceover generated: {output_path}")
                return output_path

    except Exception as e:
        print(f"[video_pro] Voiceover error: {e}")

    return None


# ==================== MAIN VIDEO GENERATION ====================

async def generate_competitor_video(
    script: str,
    title: str,
    output_path: Optional[str] = None,
    add_voiceover: bool = True
) -> Dict[str, Any]:
    """
    Generate competitor-style video (tech focus, clean aesthetic).
    """
    if not MOVIEPY_AVAILABLE:
        return {"success": False, "error": "MoviePy not installed"}

    print(f"\n{'='*80}")
    print("🎬 GENERATING COMPETITOR-STYLE VIDEO")
    print(f"{'='*80}\n")

    try:
        # Step 1: Parse script into rapid scenes
        scenes = parse_script_competitor_style(script)

        if not scenes:
            return {"success": False, "error": "No scenes parsed"}

        # Step 2: Generate voiceover
        voiceover_path = None
        if add_voiceover:
            full_text = ' '.join([s.get('text', '') for s in scenes])
            voiceover_path = await generate_voiceover_elevenlabs(full_text)

        # Step 3: Create scenes
        scene_clips = []
        for i, scene in enumerate(scenes):
            print(f"[video_pro] Creating scene {i+1}/{len(scenes)}...")
            clip = await create_competitor_scene(scene)
            scene_clips.append(clip)

        # Step 4: Concatenate with smooth transitions
        print(f"[video_pro] Combining {len(scene_clips)} scenes...")
        final_video = concatenate_videoclips(scene_clips, method="compose")

        # Step 5: Add voiceover
        if voiceover_path and os.path.exists(voiceover_path):
            try:
                audio = AudioFileClip(voiceover_path)
                if audio.duration > final_video.duration:
                    audio = audio.subclip(0, final_video.duration)
                final_video = final_video.set_audio(audio)
                print("[video_pro] ✅ Audio synced")
            except Exception as e:
                print(f"[video_pro] Audio warning: {e}")

        # Step 6: Export
        if not output_path:
            output_dir = Path(__file__).parent.parent / "output" / "videos"
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(output_dir / f"video_pro_{timestamp}.mp4")

        print(f"\n[video_pro] Exporting to: {output_path}")

        final_video.write_videofile(
            output_path,
            fps=VIDEO_FPS,
            codec='libx264',
            preset='medium',
            threads=4,
            logger='bar'
        )

        # Cleanup
        final_video.close()
        for clip in scene_clips:
            clip.close()

        print(f"\n{'='*80}")
        print("✅ VIDEO GENERATION COMPLETE!")
        print(f"{'='*80}")

        return {
            "success": True,
            "video_path": output_path,
            "duration": sum(s.get("duration", 0) for s in scenes),
            "scenes": len(scenes),
        }

    except Exception as e:
        print(f"\n❌ Video generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}
