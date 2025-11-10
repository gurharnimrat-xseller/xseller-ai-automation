"""
Competitor-Style Video Production Module
Generates viral short-form videos with:
- Scene-by-scene rendering based on script timing
- Text overlays with animations
- Stock footage backgrounds
- Professional transitions
"""

from __future__ import annotations

import os
import re
import tempfile
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Video generation imports
try:
    from moviepy.editor import (
        VideoFileClip, ColorClip, CompositeVideoClip,
        concatenate_videoclips, AudioFileClip, ImageClip
    )
    from moviepy.video.fx.all import fadein, fadeout
    import numpy as np
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("[video_production] WARNING: MoviePy not available. Install with: pip install moviepy")

import httpx
from PIL import Image, ImageDraw, ImageFont


# ==================== CONFIGURATION ====================

# API Keys
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# Video settings
VIDEO_WIDTH = 1080  # 9:16 aspect ratio for social media
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30

# Text styling
TEXT_FONT = "Arial-Bold"
TEXT_COLOR = "white"
TEXT_STROKE_COLOR = "black"
TEXT_STROKE_WIDTH = 3

# Scene durations (seconds)
DEFAULT_SCENE_DURATION = 3.0


# ==================== SCRIPT PARSING ====================

def parse_script_with_timing(script: str) -> List[Dict[str, Any]]:
    """
    Parse video script into scenes with precise timing.

    Format:
    Hook (0-2s): Text here
    Main (3-10s): Text here
    Why (11-17s): Text here
    CTA (18-20s): Text here

    Returns list of scenes with start_time, end_time, text, scene_type
    """
    scenes = []

    # Regex pattern to extract scenes with timing
    # Matches: "Hook (0-2s):", "Main (3-10s):", etc.
    pattern = r'(Hook|Main|Why|CTA)\s*\((\d+)-(\d+)s?\):\s*(.+?)(?=(?:Hook|Main|Why|CTA)\s*\(|\Z)'

    matches = re.finditer(pattern, script, re.IGNORECASE | re.DOTALL)

    for match in matches:
        scene_type = match.group(1).lower()
        start_time = int(match.group(2))
        end_time = int(match.group(3))
        text = match.group(4).strip()

        scenes.append({
            "type": scene_type,
            "start_time": start_time,
            "end_time": end_time,
            "duration": end_time - start_time,
            "text": text,
        })

    # Fallback: If no timing found, split by scene labels
    if not scenes:
        print("[video_production] No timing found, using fallback parsing")
        lines = script.split('\n')
        current_scene = None
        current_text = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line starts with scene label
            if line.lower().startswith(('hook:', 'hook ', 'main:', 'main ', 'why:', 'why ', 'cta:', 'cta ')):
                # Save previous scene
                if current_scene and current_text:
                    scenes.append({
                        "type": current_scene,
                        "text": ' '.join(current_text),
                        "duration": DEFAULT_SCENE_DURATION,
                    })

                # Start new scene
                scene_label = line.split(':')[0].strip().lower()
                current_scene = scene_label
                current_text = [line.split(':', 1)[1].strip() if ':' in line else line]
            else:
                if current_text:
                    current_text.append(line)

        # Add last scene
        if current_scene and current_text:
            scenes.append({
                "type": current_scene,
                "text": ' '.join(current_text),
                "duration": DEFAULT_SCENE_DURATION,
            })

        # Calculate start/end times for fallback
        cumulative_time = 0
        for scene in scenes:
            scene["start_time"] = cumulative_time
            scene["end_time"] = cumulative_time + scene["duration"]
            cumulative_time = scene["end_time"]

    print(f"[video_production] Parsed {len(scenes)} scenes from script")
    for i, scene in enumerate(scenes, 1):
        print(f"  Scene {i} ({scene['type']}): {scene.get('start_time', 0)}-{scene.get('end_time', 0)}s - {scene['text'][:50]}...")

    return scenes


# ==================== STOCK FOOTAGE ====================

async def get_pexels_video(query: str, duration: int = 5) -> Optional[str]:
    """
    Fetch stock video from Pexels API.

    Args:
        query: Search query (e.g., "technology", "business", "ai")
        duration: Minimum duration in seconds

    Returns:
        Video URL or None
    """
    if not PEXELS_API_KEY:
        print("[video_production] No Pexels API key configured")
        return None

    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": PEXELS_API_KEY
            }

            # Search for videos
            response = await client.get(
                "https://api.pexels.com/videos/search",
                headers=headers,
                params={
                    "query": query,
                    "per_page": 10,
                    "orientation": "portrait",  # Vertical for social media
                },
                timeout=15.0
            )

            if response.status_code == 200:
                data = response.json()
                videos = data.get("videos", [])

                # Find video with suitable duration
                for video in videos:
                    video_duration = video.get("duration", 0)
                    if video_duration >= duration:
                        # Get HD video file
                        video_files = video.get("video_files", [])
                        for file in video_files:
                            if file.get("quality") == "hd" and file.get("width") == 1080:
                                return file.get("link")

                        # Fallback: any HD video
                        for file in video_files:
                            if file.get("quality") == "hd":
                                return file.get("link")

                print(f"[video_production] No suitable video found for '{query}'")
                return None
            else:
                print(f"[video_production] Pexels API error: {response.status_code}")
                return None

    except Exception as e:
        print(f"[video_production] Error fetching Pexels video: {str(e)}")
        return None


def get_scene_keywords(scene_type: str, text: str) -> str:
    """Extract keywords for stock footage search based on scene type and text."""
    # Base keywords by scene type
    base_keywords = {
        "hook": ["technology", "innovation", "future", "digital"],
        "main": ["business", "professional", "modern", "workspace"],
        "why": ["success", "growth", "achievement", "transformation"],
        "cta": ["social media", "digital marketing", "connection", "network"],
    }

    keywords = base_keywords.get(scene_type, ["business"])

    # Extract important words from text
    important_words = ["ai", "technology", "business", "data", "innovation", "future", "success"]
    text_lower = text.lower()

    for word in important_words:
        if word in text_lower:
            return word

    return keywords[0]


# ==================== TEXT RENDERING ====================

def _load_bold_font(fontsize: int) -> ImageFont.FreeTypeFont:
    """
    Load a bold font, trying multiple common paths.
    Falls back to default if none found.
    """
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
        "C:\\Windows\\Fonts\\arialbd.ttf",  # Windows
    ]

    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, fontsize)
            except Exception:
                continue

    # Fallback to default font
    try:
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()


def create_text_image_pil(
    text: str,
    fontsize: int,
    color: str = "white",
    stroke_color: str = "black",
    stroke_width: int = 3,
    size: Tuple[int, int] = (VIDEO_WIDTH, VIDEO_HEIGHT),
    max_width: int = None
) -> Image.Image:
    """
    Create text image using PIL (no ImageMagick required).
    """
    if max_width is None:
        max_width = size[0] - 100  # Default padding

    # Create transparent image
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Load font
    font = _load_bold_font(fontsize)

    # Handle multi-line text (text already formatted with \n)
    lines = text.split('\n')

    # Calculate total height
    line_heights = []
    line_widths = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])

    total_height = sum(line_heights) + (len(lines) - 1) * 20  # 20px spacing

    # Start position (centered vertically)
    start_y = (size[1] - total_height) // 2

    # Draw each line
    current_y = start_y
    for line, line_width, line_height in zip(lines, line_widths, line_heights):
        x = (size[0] - line_width) // 2

        # Draw stroke (outline)
        if stroke_width > 0:
            for adj_x in range(-stroke_width, stroke_width + 1):
                for adj_y in range(-stroke_width, stroke_width + 1):
                    draw.text((x + adj_x, current_y + adj_y), line, font=font, fill=stroke_color)

        # Draw main text
        draw.text((x, current_y), line, font=font, fill=color)

        current_y += line_height + 20

    # Convert RGBA to RGB for MoviePy compatibility
    # Create a black background and composite the RGBA image on it
    rgb_img = Image.new('RGB', size, (0, 0, 0))
    rgb_img.paste(img, (0, 0), img)  # Use img as mask for transparency

    return rgb_img


def create_text_clip(
    text: str,
    duration: float,
    size: Tuple[int, int] = (VIDEO_WIDTH, VIDEO_HEIGHT),
    fontsize: int = 80,
    color: str = TEXT_COLOR,
    position: str = "center",
) -> ImageClip:
    """
    Create animated text clip with styling using PIL (no ImageMagick required).

    Args:
        text: Text to display
        duration: Duration in seconds
        size: (width, height) tuple
        fontsize: Font size in points
        color: Text color
        position: Position ('center', 'top', 'bottom')

    Returns:
        ImageClip object
    """
    if not MOVIEPY_AVAILABLE:
        raise ImportError("MoviePy not available")

    # Split long text into multiple lines
    words = text.split()
    lines = []
    current_line = []
    max_chars_per_line = 25

    for word in words:
        current_line.append(word)
        line_text = ' '.join(current_line)
        if len(line_text) > max_chars_per_line:
            if len(current_line) > 1:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(line_text)
                current_line = []

    if current_line:
        lines.append(' '.join(current_line))

    formatted_text = '\n'.join(lines)

    # Create text image using PIL (no ImageMagick needed)
    text_img = create_text_image_pil(
        text=formatted_text,
        fontsize=fontsize,
        color=color,
        stroke_color=TEXT_STROKE_COLOR,
        stroke_width=TEXT_STROKE_WIDTH,
        size=size,
        max_width=size[0] - 100  # Padding
    )

    # Convert PIL image to ImageClip
    txt_clip = ImageClip(np.array(text_img)).set_duration(duration)

    # Position text
    if position == "center":
        txt_clip = txt_clip.set_position('center')
    elif position == "top":
        txt_clip = txt_clip.set_position(('center', 100))
    elif position == "bottom":
        txt_clip = txt_clip.set_position(('center', size[1] - 300))

    # Add fade in/out animations
    txt_clip = txt_clip.crossfadein(0.3)

    if duration > 0.5:
        txt_clip = txt_clip.crossfadeout(0.3)

    return txt_clip


# ==================== SCENE GENERATION ====================

async def create_scene(
    scene: Dict[str, Any],
    output_size: Tuple[int, int] = (VIDEO_WIDTH, VIDEO_HEIGHT)
) -> CompositeVideoClip:
    """
    Create a single scene with background and text overlay.

    Args:
        scene: Scene dict with type, text, duration
        output_size: Output video dimensions

    Returns:
        CompositeVideoClip
    """
    if not MOVIEPY_AVAILABLE:
        raise ImportError("MoviePy not available")

    duration = scene.get("duration", DEFAULT_SCENE_DURATION)
    text = scene.get("text", "")
    scene_type = scene.get("type", "main")

    print(f"[video_production] Creating scene: {scene_type} ({duration}s)")

    # Scene colors based on type
    scene_colors = {
        "hook": "#FF0050",  # Vibrant red/pink
        "main": "#0066FF",  # Blue
        "why": "#00D9FF",   # Cyan
        "cta": "#00FF88",   # Green
    }

    bg_color = scene_colors.get(scene_type, "#1a1a2e")

    # Try to get stock footage
    keywords = get_scene_keywords(scene_type, text)
    stock_video_url = await get_pexels_video(keywords, duration)

    # Create background
    if stock_video_url:
        try:
            # Download and use stock video
            temp_video = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            async with httpx.AsyncClient() as client:
                response = await client.get(stock_video_url, timeout=30.0)
                temp_video.write(response.content)
                temp_video.close()

            bg_clip = VideoFileClip(temp_video.name)

            # Trim to required duration
            if bg_clip.duration > duration:
                bg_clip = bg_clip.subclip(0, duration)

            # Resize to fit
            bg_clip = bg_clip.resize(output_size)

            # Apply color overlay for brand consistency
            overlay = ColorClip(size=output_size, color=bg_color, duration=duration).set_opacity(0.4)
            bg_clip = CompositeVideoClip([bg_clip, overlay])

            # Clean up temp file
            os.unlink(temp_video.name)

            print(f"[video_production] Using stock footage for {scene_type}")
        except Exception as e:
            print(f"[video_production] Failed to load stock video: {e}, using color background")
            bg_clip = ColorClip(size=output_size, color=bg_color, duration=duration)
    else:
        # Fallback: solid color background
        bg_clip = ColorClip(size=output_size, color=bg_color, duration=duration)
        print(f"[video_production] Using color background for {scene_type}")

    # Create text overlay
    fontsize = {
        "hook": 90,  # Larger for hook
        "main": 70,
        "why": 70,
        "cta": 80,
    }.get(scene_type, 70)

    text_clip = create_text_clip(
        text=text,
        duration=duration,
        size=output_size,
        fontsize=fontsize,
        position="center"
    )

    # Composite scene
    scene_clip = CompositeVideoClip([bg_clip, text_clip], size=output_size)

    return scene_clip


# ==================== VOICEOVER GENERATION ====================

async def generate_voiceover_elevenlabs(
    text: str,
    output_path: Optional[str] = None
) -> Optional[str]:
    """
    Generate voiceover using Eleven Labs API.

    Args:
        text: Script text to convert to speech
        output_path: Optional output file path

    Returns:
        Path to generated audio file or None
    """
    if not ELEVENLABS_API_KEY:
        print("[video_production] Eleven Labs API key not configured")
        return None

    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            }

            # Use default voice (Rachel) - professional, clear
            voice_id = "21m00Tcm4TlvDq8ikWAM"

            # Generate speech
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }

            print(f"[video_production] Generating voiceover ({len(text)} chars)...")

            response = await client.post(
                url,
                headers=headers,
                json=payload,
                timeout=60.0
            )

            if response.status_code == 200:
                # Save audio file
                if not output_path:
                    audio_dir = Path(__file__).parent.parent / "output" / "audio"
                    audio_dir.mkdir(parents=True, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_path = str(audio_dir / f"voiceover_{timestamp}.mp3")

                with open(output_path, "wb") as f:
                    f.write(response.content)

                print(f"[video_production] ✅ Voiceover saved to {output_path}")
                return output_path
            else:
                print(f"[video_production] Eleven Labs API error: {response.status_code} - {response.text}")
                return None

    except Exception as e:
        print(f"[video_production] Error generating voiceover: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


# ==================== VIDEO ASSEMBLY ====================

async def generate_video_from_script(
    script: str,
    title: str,
    output_path: Optional[str] = None,
    add_voiceover: bool = True
) -> Dict[str, Any]:
    """
    Generate complete video from script.

    Args:
        script: Video script with timing
        title: Video title
        output_path: Optional output file path

    Returns:
        Dict with success status and file path
    """
    if not MOVIEPY_AVAILABLE:
        return {
            "success": False,
            "error": "MoviePy not installed. Run: pip install moviepy"
        }

    print(f"[video_production] Starting video generation for: {title}")

    try:
        # Step 1: Parse script
        scenes = parse_script_with_timing(script)

        if not scenes:
            return {
                "success": False,
                "error": "No scenes found in script"
            }

        # Step 2: Generate scenes
        scene_clips = []
        for scene in scenes:
            scene_clip = await create_scene(scene)
            scene_clips.append(scene_clip)

        # Step 3: Generate voiceover (if enabled)
        voiceover_path = None
        if add_voiceover:
            # Extract full text from script (remove timing labels)
            full_text = ' '.join([scene.get('text', '') for scene in scenes])
            voiceover_path = await generate_voiceover_elevenlabs(full_text)

        # Step 4: Concatenate scenes
        print(f"[video_production] Concatenating {len(scene_clips)} scenes...")
        final_video = concatenate_videoclips(scene_clips, method="compose")

        # Step 5: Add voiceover audio
        if voiceover_path and os.path.exists(voiceover_path):
            try:
                audio_clip = AudioFileClip(voiceover_path)
                # Match audio duration to video (trim or extend as needed)
                if audio_clip.duration > final_video.duration:
                    audio_clip = audio_clip.subclip(0, final_video.duration)
                final_video = final_video.set_audio(audio_clip)
                print(f"[video_production] ✅ Voiceover added to video")
            except Exception as e:
                print(f"[video_production] Warning: Could not add audio: {e}")

        # Step 6: Export video
        if not output_path:
            output_dir = Path(__file__).parent.parent / "output" / "videos"
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(output_dir / f"video_{timestamp}.mp4")

        print(f"[video_production] Exporting video to: {output_path}")

        final_video.write_videofile(
            output_path,
            fps=VIDEO_FPS,
            codec='libx264',
            audio=False,  # No audio for now
            preset='medium',
            threads=4,
            logger='bar'
        )

        # Clean up
        final_video.close()
        for clip in scene_clips:
            clip.close()

        print(f"[video_production] ✅ Video generated successfully: {output_path}")

        return {
            "success": True,
            "video_path": output_path,
            "duration": sum(s.get("duration", 0) for s in scenes),
            "scenes": len(scenes),
        }

    except Exception as e:
        print(f"[video_production] ❌ Video generation failed: {str(e)}")
        import traceback
        traceback.print_exc()

        return {
            "success": False,
            "error": str(e)
        }
