"""
Text rendering utilities using PIL (no ImageMagick required)
Provides TextClip-like functionality without external dependencies
"""
from agents.checks.router import should_offload, offload_to_gemini  # noqa: F401

import os
import numpy as np
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont

try:
    from moviepy.editor import ImageClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False


def create_text_clip_pil(
    text: str,
    fontsize: int = 70,
    color: str = "white",
    stroke_color: str = "black",
    stroke_width: int = 3,
    bg_color: Optional[Tuple[int, int, int, int]] = None,
    size: Tuple[int, int] = (1080, 1920),
    duration: float = 3.0,
) -> 'ImageClip':
    """
    Create a text clip using PIL (replacement for MoviePy's TextClip).

    Args:
        text: Text to render
        fontsize: Font size in points
        color: Text color (name or hex)
        stroke_color: Outline color
        stroke_width: Outline width in pixels
        bg_color: Background color tuple (R, G, B, A) or None for transparent
        size: Video size (width, height)
        duration: Clip duration in seconds

    Returns:
        MoviePy ImageClip with the rendered text
    """
    if not MOVIEPY_AVAILABLE:
        raise ImportError("MoviePy not available")

    # Create image with transparent or colored background
    if bg_color is None:
        img = Image.new('RGBA', size, (0, 0, 0, 0))
    else:
        img = Image.new('RGBA', size, bg_color)

    draw = ImageDraw.Draw(img)

    # Load font
    font = _load_bold_font(fontsize)

    # Handle multi-line text
    lines = text.split('\n')

    # Calculate total text height
    line_heights = []
    line_widths = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])

    total_height = sum(line_heights) + (len(lines) - 1) * 20  # 20px spacing
    max_width = max(line_widths)

    # Start position (centered)
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

    # Convert to MoviePy ImageClip
    clip = ImageClip(np.array(img)).set_duration(duration)

    return clip


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
        # Last resort: create a basic font
        return ImageFont.load_default()
