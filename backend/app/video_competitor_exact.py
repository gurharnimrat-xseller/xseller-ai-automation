"""
EXACT COMPETITOR VIDEO REPLICATION
30-second structure matching viral tech shorts

Structure:
0-3s:   Hook (Question + Shocking visual)
3-9s:   Demo (Tool showcase)
9-18s:  Proof (Before/After + Stats)
18-24s: Impact (Transformation message)
24-30s: CTA (Link in bio)
"""
from __future__ import annotations
from agents.checks.router import should_offload, offload_to_gemini  # guardrails


import os
import tempfile
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

try:
    from moviepy.editor import (
        VideoFileClip, ColorClip, CompositeVideoClip,
        concatenate_videoclips, AudioFileClip, ImageClip
    )
    from moviepy.video.fx.all import fadein, fadeout, resize
    import numpy as np
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

from PIL import Image, ImageDraw, ImageFont
import httpx


# ==================== CONFIGURATION ====================

# API Keys
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# Video settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30

# EXACT COMPETITOR TEXT STYLES
TEXT_STYLES = {
    "hook": {
        "font": "Arial-Bold",
        "size": 90,
        "color": "white",
        "stroke_color": "black",
        "stroke_width": 3,
        "position": "center",  # Center of screen
    },
    "demo": {
        "font": "Arial-Bold",
        "size": 50,
        "color": "white",
        "stroke_color": "black",
        "stroke_width": 2,
        "position": "top",  # Top of screen
    },
    "stats": {
        "font": "Arial-Bold",
        "size": 70,
        "color": "#00FF00",  # Green
        "stroke_color": "black",
        "stroke_width": 3,
        "position": "center",
    },
    "impact": {
        "font": "Arial-Bold",
        "size": 80,
        "color": "#FFD700",  # Yellow
        "stroke_color": "black",
        "stroke_width": 3,
        "position": "center",
    },
    "cta": {
        "font": "Arial-Bold",
        "size": 55,
        "color": "white",
        "stroke_color": "black",
        "stroke_width": 2,
        "position": "bottom",  # Lower third
    }
}

# Color schemes
COLORS = {
    "dark_bg": "#0A0E1A",
    "tech_blue": "#0066FF",
    "tech_purple": "#6B46FF",
}


# ==================== SCRIPT PARSING ====================

def parse_30s_structure(script: str, title: str) -> List[Dict[str, Any]]:
    """
    Parse script into exact 30-second competitor structure.

    Returns 5 scenes:
    1. Hook (0-3s): Question hook
    2. Demo (3-9s): Tool showcase
    3. Proof (9-18s): Before/after + stats
    4. Impact (18-24s): Transformation message
    5. CTA (24-30s): Call to action
    """

    # Try to extract from formatted script
    scenes_data = {
        "hook": {"text": "", "duration": 3, "start": 0},
        "demo": {"text": "", "duration": 6, "start": 3},
        "proof": {"text": "", "duration": 9, "start": 9},
        "impact": {"text": "", "duration": 6, "start": 18},
        "cta": {"text": "", "duration": 6, "start": 24},
    }

    # Parse script sections
    lines = script.split('\n')
    current_section = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        line_lower = line.lower()

        if 'hook' in line_lower or line_lower.startswith('0'):
            current_section = 'hook'
            # Extract text after colon
            if ':' in line:
                scenes_data['hook']['text'] = line.split(':', 1)[1].strip()
        elif 'demo' in line_lower or line_lower.startswith('3') or 'tool' in line_lower:
            current_section = 'demo'
            if ':' in line:
                scenes_data['demo']['text'] = line.split(':', 1)[1].strip()
        elif 'proof' in line_lower or line_lower.startswith('9') or 'before' in line_lower or 'after' in line_lower:
            current_section = 'proof'
            if ':' in line:
                scenes_data['proof']['text'] = line.split(':', 1)[1].strip()
        elif 'impact' in line_lower or line_lower.startswith('18') or 'changes' in line_lower or 'why' in line_lower:
            current_section = 'impact'
            if ':' in line:
                scenes_data['impact']['text'] = line.split(':', 1)[1].strip()
        elif 'cta' in line_lower or line_lower.startswith('24') or 'link' in line_lower or 'follow' in line_lower:
            current_section = 'cta'
            if ':' in line:
                scenes_data['cta']['text'] = line.split(':', 1)[1].strip()
        elif current_section and ':' not in line:
            # Continuation of current section
            if scenes_data[current_section]['text']:
                scenes_data[current_section]['text'] += ' ' + line
            else:
                scenes_data[current_section]['text'] = line

    # Fallback defaults if sections are empty
    if not scenes_data['hook']['text']:
        scenes_data['hook']['text'] = f"CAN AI DO THIS? {title}"
    if not scenes_data['demo']['text']:
        scenes_data['demo']['text'] = f"Meet {title}"
    if not scenes_data['proof']['text']:
        scenes_data['proof']['text'] = "10X faster results. Zero coding needed."
    if not scenes_data['impact']['text']:
        scenes_data['impact']['text'] = "THIS CHANGES EVERYTHING"
    if not scenes_data['cta']['text']:
        scenes_data['cta']['text'] = "LINK IN BIO 👇 Follow for more AI tips"

    # Convert to scene list
    scenes = []
    for scene_type, data in scenes_data.items():
        scenes.append({
            "type": scene_type,
            "text": data["text"],
            "duration": data["duration"],
            "start_time": data["start"],
            "end_time": data["start"] + data["duration"],
        })

    print(f"[competitor] Parsed 30s structure with {len(scenes)} scenes")
    for scene in scenes:
        print(f"  {scene['type']}: {scene['start_time']}-{scene['end_time']}s - {scene['text'][:50]}...")

    return scenes


# ==================== TEXT CREATION ====================

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

    # Handle multi-line text wrapping
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        test_width = bbox[2] - bbox[0]

        if test_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

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


def create_text_exact_style(
    text: str,
    style_name: str,
    duration: float,
    size: Tuple[int, int] = (VIDEO_WIDTH, VIDEO_HEIGHT)
) -> ImageClip:
    """
    Create text with EXACT competitor styling using PIL (no ImageMagick required).
    """
    if not MOVIEPY_AVAILABLE:
        raise ImportError("MoviePy not available")

    style = TEXT_STYLES.get(style_name, TEXT_STYLES["demo"])

    try:
        # Create text image using PIL
        text_img = create_text_image_pil(
            text=text,
            fontsize=style["size"],
            color=style["color"],
            stroke_color=style["stroke_color"],
            stroke_width=style["stroke_width"],
            size=size,
            max_width=size[0] - 100  # Padding
        )

        # Convert PIL image to ImageClip
        txt = ImageClip(np.array(text_img)).set_duration(duration)

        # Position based on style
        position = style["position"]
        if position == "center":
            txt = txt.set_position('center')
        elif position == "top":
            txt = txt.set_position(('center', 100))
        elif position == "bottom":
            # Lower third
            txt = txt.set_position(('center', size[1] - 250))

        # Animations
        txt = txt.crossfadein(0.2)
        if duration > 0.5:
            txt = txt.crossfadeout(0.2)

        return txt

    except Exception as e:
        print(f"[competitor] Error creating text: {e}")
        # Fallback: simple text with PIL
        text_img = create_text_image_pil(
            text=text,
            fontsize=60,
            color='white',
            stroke_color='black',
            stroke_width=2,
            size=size
        )
        txt = ImageClip(np.array(text_img)).set_duration(duration)
        txt = txt.set_position('center')
        return txt


# ==================== SMART VIDEO FETCHING ====================

def extract_smart_keywords(text: str, title: str) -> List[str]:
    """
    Extract SPECIFIC keywords from news script for relevant video search.
    Returns specific terms, not generic AI keywords.
    """
    import re

    keywords = []

    # Extract company/product names (capitalized words)
    proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text + " " + title)
    keywords.extend(proper_nouns[:3])

    # Extract key technical terms
    tech_terms = ['GPT', 'Claude', 'Gemini', 'ChatGPT', 'Midjourney', 'DALL-E', 'Stable Diffusion',
                  'API', 'model', 'robot', 'automation', 'coding', 'vision', 'voice', 'image']

    for term in tech_terms:
        if term.lower() in text.lower() or term.lower() in title.lower():
            keywords.append(term)

    # Extract action words specific to the content
    action_words = ['coding', 'writing', 'generating', 'creating', 'analyzing', 'processing',
                    'designing', 'editing', 'translating', 'summarizing']

    for action in action_words:
        if action in text.lower():
            keywords.append(action)

    # If we have specific keywords, return them
    if keywords:
        return keywords[:3]  # Top 3 most relevant

    # Fallback to title words
    title_words = [w for w in title.split() if len(w) > 4]
    return title_words[:2] if title_words else ['technology', 'innovation']


async def fetch_relevant_pexels_video(keywords: List[str], duration: int = 5) -> Optional[str]:
    """
    Fetch SPECIFIC video from Pexels based on script keywords.
    """
    if not PEXELS_API_KEY:
        print("[competitor] No Pexels API key, using solid colors")
        return None

    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": PEXELS_API_KEY}

            # Try each keyword combination
            search_queries = [
                ' '.join(keywords),  # All keywords together
                keywords[0] if keywords else 'technology',  # First keyword
                f"{keywords[0]} demo" if keywords else 'tech demo',  # Keyword + demo
            ]

            for query in search_queries:
                print(f"[competitor] Searching Pexels for: '{query}'")

                response = await client.get(
                    "https://api.pexels.com/videos/search",
                    headers=headers,
                    params={
                        "query": query,
                        "per_page": 5,
                        "orientation": "portrait",
                    },
                    timeout=15.0
                )

                if response.status_code == 200:
                    data = response.json()
                    videos = data.get("videos", [])

                    for video in videos:
                        if video.get("duration", 0) >= duration:
                            # Get HD video file
                            for file in video.get("video_files", []):
                                if file.get("quality") == "hd" and file.get("width") == 1080:
                                    print(f"[competitor] ✅ Found relevant video for '{query}'")
                                    return file.get("link")

            print(f"[competitor] No specific video found, using solid background")
            return None

    except Exception as e:
        print(f"[competitor] Pexels error: {e}")
        return None


# ==================== SCENE CREATION ====================

async def create_competitor_scene(
    scene: Dict[str, Any],
    title: str = "",
    size: Tuple[int, int] = (VIDEO_WIDTH, VIDEO_HEIGHT),
    use_specific_footage: bool = True
) -> CompositeVideoClip:
    """
    Create scene matching exact competitor style.
    """
    if not MOVIEPY_AVAILABLE:
        raise ImportError("MoviePy not available")

    scene_type = scene.get("type", "demo")
    text = scene.get("text", "")
    duration = scene.get("duration", 3.0)

    print(f"[competitor] Creating {scene_type} scene ({duration}s)")

    # Background colors per scene type
    bg_colors = {
        "hook": "#FF0050",  # Vibrant red
        "demo": "#0066FF",  # Tech blue
        "proof": "#6B46FF",  # Purple
        "impact": "#00D9FF",  # Cyan
        "cta": "#00FF88",  # Green
    }

    bg_color = bg_colors.get(scene_type, COLORS["dark_bg"])

    # Try to get RELEVANT stock footage based on script content
    bg = None
    if use_specific_footage:
        keywords = extract_smart_keywords(text, title)
        print(f"[competitor] Keywords for {scene_type}: {keywords}")

        video_url = await fetch_relevant_pexels_video(keywords, duration)

        if video_url:
            try:
                # Download video
                temp_video = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
                async with httpx.AsyncClient() as client:
                    response = await client.get(video_url, timeout=30.0)
                    temp_video.write(response.content)
                    temp_video.close()

                # Load and process video
                video_clip = VideoFileClip(temp_video.name)

                # Trim to duration
                if video_clip.duration > duration:
                    video_clip = video_clip.subclip(0, duration)

                # Resize to fit
                video_clip = video_clip.resize(size)

                # Add color overlay for brand consistency (30% opacity)
                overlay = ColorClip(size=size, color=bg_color, duration=duration).set_opacity(0.3)
                bg = CompositeVideoClip([video_clip, overlay])

                # Clean up temp file
                os.unlink(temp_video.name)

                print(f"[competitor] ✅ Using relevant footage for {scene_type}")
            except Exception as e:
                print(f"[competitor] Could not load video: {e}")
                bg = None

    # Fallback: solid color background
    if bg is None:
        bg = ColorClip(size=size, color=bg_color, duration=duration)
        print(f"[competitor] Using solid background for {scene_type}")

    # Create text with exact style
    text_clip = create_text_exact_style(
        text=text,
        style_name=scene_type,
        duration=duration,
        size=size
    )

    # Composite
    final = CompositeVideoClip([bg, text_clip], size=size)

    return final


# ==================== VOICEOVER ====================

async def generate_voiceover(text: str) -> Optional[str]:
    """Generate voiceover with Eleven Labs."""
    if not ELEVENLABS_API_KEY:
        return None

    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            }

            voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel - clear, professional
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.6,  # Slightly more stable for clarity
                    "similarity_boost": 0.8,
                    "style": 0.2,  # Slight expressiveness
                }
            }

            print("[competitor] Generating voiceover...")

            response = await client.post(url, headers=headers, json=payload, timeout=60.0)

            if response.status_code == 200:
                audio_dir = Path(__file__).parent.parent / "output" / "audio"
                audio_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = str(audio_dir / f"voice_{timestamp}.mp3")

                with open(output_path, "wb") as f:
                    f.write(response.content)

                print(f"[competitor] ✅ Voiceover saved: {output_path}")
                return output_path
            else:
                print(f"[competitor] Voiceover API error: {response.status_code}")
                return None

    except Exception as e:
        print(f"[competitor] Voiceover error: {e}")
        return None


# ==================== MAIN VIDEO GENERATION ====================

async def generate_exact_competitor_video(
    script: str,
    title: str,
    output_path: Optional[str] = None,
    add_voiceover: bool = True
) -> Dict[str, Any]:
    """
    Generate EXACT 30-second competitor-style video.

    Matches viral tech shorts structure perfectly.
    """
    if not MOVIEPY_AVAILABLE:
        return {"success": False, "error": "MoviePy not installed"}

    print(f"\n{'='*80}")
    print(f"🎬 GENERATING EXACT COMPETITOR VIDEO (30s)")
    print(f"Title: {title}")
    print(f"{'='*80}\n")

    try:
        # Step 1: Parse into 30s structure
        scenes = parse_30s_structure(script, title)

        # Step 2: Generate voiceover
        voiceover_path = None
        if add_voiceover:
            full_text = ' '.join([s.get('text', '') for s in scenes])
            voiceover_path = await generate_voiceover(full_text)

        # Step 3: Create all 5 scenes with RELEVANT footage
        scene_clips = []
        for i, scene in enumerate(scenes):
            print(f"\n[competitor] Creating scene {i+1}/5: {scene['type'].upper()}")
            clip = await create_competitor_scene(
                scene=scene,
                title=title,  # Pass title for smart keyword extraction
                use_specific_footage=True  # Enable relevant video matching
            )
            scene_clips.append(clip)

        # Step 4: Concatenate scenes
        print(f"\n[competitor] Assembling {len(scene_clips)} scenes...")
        final_video = concatenate_videoclips(scene_clips, method="compose")

        # Step 5: Add voiceover
        if voiceover_path and os.path.exists(voiceover_path):
            try:
                audio = AudioFileClip(voiceover_path)

                # Trim or extend audio to match video
                if audio.duration > final_video.duration:
                    audio = audio.subclip(0, final_video.duration)
                elif audio.duration < final_video.duration:
                    # Speed up slightly if audio is too short
                    speed_factor = audio.duration / final_video.duration
                    if speed_factor > 0.9:  # Only if close
                        audio = audio.fx(lambda clip: clip.speedx(1 / speed_factor))

                final_video = final_video.set_audio(audio)
                print("[competitor] ✅ Voiceover synced to video")
            except Exception as e:
                print(f"[competitor] Audio warning: {e}")

        # Step 6: Export
        if not output_path:
            output_dir = Path(__file__).parent.parent / "output" / "videos"
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(output_dir / f"competitor_{timestamp}.mp4")

        print(f"\n[competitor] Exporting final video to: {output_path}")
        print("[competitor] This may take 2-3 minutes...")

        final_video.write_videofile(
            output_path,
            fps=VIDEO_FPS,
            codec='libx264',
            preset='medium',
            threads=4,
            logger='bar',
            audio_codec='aac'
        )

        # Cleanup
        final_video.close()
        for clip in scene_clips:
            clip.close()

        print(f"\n{'='*80}")
        print(f"✅ COMPETITOR VIDEO COMPLETE!")
        print(f"{'='*80}")
        print(f"📍 Location: {output_path}")
        print(f"⏱️  Duration: 30 seconds")
        print(f"🎬 Scenes: 5 (Hook → Demo → Proof → Impact → CTA)")
        print(f"{'='*80}\n")

        return {
            "success": True,
            "video_path": output_path,
            "duration": 30,
            "scenes": 5,
            "structure": "Hook/Demo/Proof/Impact/CTA"
        }

    except Exception as e:
        print(f"\n❌ VIDEO GENERATION FAILED")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

        return {
            "success": False,
            "error": str(e)
        }
