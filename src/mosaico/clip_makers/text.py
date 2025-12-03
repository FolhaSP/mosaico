from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import numpy as np
from find_system_fonts_filename import get_system_fonts_filename
from moviepy.Clip import Clip
from moviepy.video.VideoClip import ImageClip
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from mosaico.assets.text import BaseTextAsset
from mosaico.clip_makers.base import BaseClipMaker
from mosaico.positioning.utils import is_relative_position


RGBAColor = tuple[int, int, int, int | float]


class TextClipMaker(BaseClipMaker[BaseTextAsset]):
    """
    A clip maker for text assets.

    The process of text clip creation involves:

    1. Font and Text Preparation:
        - Loads system fonts using the specified font family
        - Wraps text to fit within video width
        - Calculates text dimensions

    2. Shadow Creation (if enabled):
        - Generates shadow layer with specified angle and distance
        - Applies blur effect and opacity
        - Handles shadow color and positioning

    3. Text Rendering:
        - Creates text layer with specified font and color
        - Applies stroke/outline effects
        - Handles text alignment and line height
        - Supports RGBA colors with transparency

    4. Image Composition:
        - Combines shadow and text layers if shadow enabled
        - Crops image to text boundaries
        - Creates temporary PNG file for MoviePy

    5. Clip Creation:
        - Converts rendered image to MoviePy clip
        - Sets position based on text parameters
        - Applies specified duration

    __Examples__:

    ```python
    # Create a basic text clip
    maker = TextClipMaker(duration=5.0, video_resolution=(1920, 1080))
    clip = maker.make_clip(text_asset)

    # Create clip with shadow
    text_asset.params.has_shadow = True
    clip = maker.make_clip(text_asset)  # Will add shadow effect

    # Create clip with custom position
    text_asset.params.position = AbsolutePosition(x=100, y=50)
    clip = maker.make_clip(text_asset)  # Will position at x=100, y=50

    # Create clip with custom font size
    text_asset.params.font_size = 48
    clip = maker.make_clip(text_asset)  # Will render text with font size 48
    ```
    """

    def _make_clip(self, asset: BaseTextAsset) -> Clip:
        """
        Make a clip from the given asset content.

        :param asset: The text asset.
        :param duration: The duration of the clip.
        :param video_resolution: The resolution of the video.
        :return: The text clip.
        """
        if self.video_resolution is None:
            raise ValueError("video_resolution is required to make a text clip")

        if self.duration is None:
            raise ValueError("duration is required to make a text clip")

        params = asset.params

        if params.font_family is None:
            params.font_family = _get_system_fallback_font_name()

        max_width, _ = self.video_resolution

        # Load the font and wrap the text
        font = _load_font(params.font_family, params.font_size)
        text = asset.to_string()
        wrapped_text = _wrap_text(text, font, round(max_width * 0.9), params.stroke_width)
        text_size = _get_font_text_size(
            wrapped_text, font, line_height=params.line_height, stroke_width=params.stroke_width, align=params.align
        )

        # Ensure text size has minimum dimensions to avoid PIL errors with zero-sized images
        text_size = (max(text_size[0], 1), max(text_size[1], 1))

        shadow_image = None

        if asset.has_shadow:
            shadow_image = _draw_text_shadow_image(
                text=wrapped_text,
                text_size=text_size,
                font=font,
                line_height=params.line_height,
                align=params.align,
                shadow_color=params.shadow_color.as_hex(),
                shadow_blur=params.shadow_blur,
                shadow_angle=params.shadow_angle,
                shadow_opacity=params.shadow_opacity,
                shadow_distance=params.shadow_distance,
            )

        font_color = cast(RGBAColor, params.font_color.as_rgb_tuple(alpha=True))

        text_image = _draw_text_image(
            text=wrapped_text,
            text_size=text_size,
            font=font,
            line_height=params.line_height,
            font_color=font_color,
            stroke_color=params.stroke_color.as_hex(),
            stroke_width=params.stroke_width,
            align=params.align,
        )

        if shadow_image is not None:
            if shadow_image.size != text_image.size:
                final_image = shadow_image.copy()
                final_image.paste(text_image, (0, 0), text_image)
            else:
                final_image = Image.alpha_composite(shadow_image, text_image)
        else:
            final_image = text_image.copy()

        bbox = final_image.getbbox()
        final_image = final_image.crop(bbox)
        np_image = np.asarray(final_image)

        return (
            ImageClip(np_image)
            .with_position((params.position.x, params.position.y), relative=is_relative_position(params.position))
            .with_duration(self.duration)
        )


@dataclass
class SystemFont:
    """System font representation."""

    path: str
    """The path to the font file in the system."""

    @property
    def name(self) -> str:
        """
        Get the font name.
        """
        return Path(self.path).with_suffix("").name

    @property
    def slug(self) -> str:
        """
        Get the slugified font name.
        """
        return _slugify_font_name(self.name)

    def matches(self, name: str) -> bool:
        """
        Check if the font name matches the given name.
        """
        return self.name == name or self.slug == _slugify_font_name(name)

    def load(self, size: float) -> ImageFont.FreeTypeFont:
        """
        Load the font.
        """
        return ImageFont.truetype(self.path, size)


def _slugify_font_name(font_name: str) -> str:
    """
    Get the slugified font name.

    Slugify the font name by converting to lowercase, removing special characters,
    and replacing spaces and underscores with hyphens.
    """
    # Convert to lowercase and replace spaces/underscores with hyphens
    slug = font_name.lower().replace(" ", "-").replace("_", "-")

    # Remove any non-alphanumeric characters except hyphens
    slug = "".join(c for c in slug if c.isalnum() or c == "-")

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    # Replace multiple consecutive hyphens with a single hyphen
    while "--" in slug:
        slug = slug.replace("--", "-")

    return slug


def _list_system_fonts() -> list[SystemFont]:
    """
    List the system fonts.
    """
    return [SystemFont(path=path) for path in get_system_fonts_filename()]


def _get_system_fallback_font_name() -> str:
    """
    Get the system fallback font name.
    """
    if sys.platform == "win32":
        return "Arialbd"
    elif sys.platform == "darwin":
        return "Arial Bold"
    else:
        return "DejaVuSans-Bold"


def _load_font(font_family: str, font_size: int) -> ImageFont.FreeTypeFont:
    """
    Load the font with the given family and size.
    """
    available_fonts = _list_system_fonts()
    selected_font = next((font for font in available_fonts if font.matches(font_family)), None)

    if selected_font is not None:
        return selected_font.load(font_size)

    default_font = ImageFont.load_default(font_size)
    default_font = cast(ImageFont.FreeTypeFont, default_font)
    return default_font


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, stroke_width: float = 0) -> str:
    """
    Wrap the given text to fit within the given width.
    """
    lines = []
    for line in text.split("\n"):
        stripped_line = line.rstrip()
        if _get_font_text_size(stripped_line, font, stroke_width=stroke_width)[0] <= max_width:
            lines.append(stripped_line)
            continue

        words = stripped_line.split(" ")
        wrapped_line_words: list[str] = []

        for word in words:
            candidate_line = " ".join([*wrapped_line_words, word])
            if _get_font_text_size(candidate_line, font, stroke_width=stroke_width)[0] <= max_width:
                wrapped_line_words.append(word)
                continue

            if _get_font_text_size(word, font, stroke_width=stroke_width)[0] > max_width:
                for chunk in _split_long_word(word, font, max_width, stroke_width):
                    candidate_chunk_line = " ".join([*wrapped_line_words, chunk])
                    if wrapped_line_words and _get_font_text_size(candidate_chunk_line, font, stroke_width=stroke_width)[0] > max_width:
                        lines.append(" ".join(wrapped_line_words))
                        wrapped_line_words = [chunk]
                    else:
                        wrapped_line_words.append(chunk)
                continue

            if wrapped_line_words:
                lines.append(" ".join(wrapped_line_words))
            wrapped_line_words = [word]

        if wrapped_line_words:
            lines.append(" ".join(wrapped_line_words))

    balanced_lines = _rebalance_wrapped_lines(lines, font, max_width, stroke_width)
    return "\n".join(balanced_lines)


def _split_long_word(word: str, font: ImageFont.FreeTypeFont, max_width: int, stroke_width: float = 0) -> list[str]:
    """
    Split a word longer than max width into chunks.
    """
    if not word:
        return [word]

    parts: list[str] = []
    current = ""
    for char in word:
        candidate = current + char
        if _get_font_text_size(candidate, font, stroke_width=stroke_width)[0] <= max_width or not current:
            current = candidate
            continue

        parts.append(current)
        current = char

    if current:
        parts.append(current)

    return parts


def _get_font_text_size(
    text: str, font: ImageFont.FreeTypeFont, line_height: int = 0, stroke_width: float = 0, align: str = "left"
) -> tuple[int, int]:
    """
    Get the width and height of the text with the given font.
    """
    bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).multiline_textbbox(
        (0, 0), text, font=font, spacing=line_height, align=align, stroke_width=round(stroke_width)
    )
    return round(bbox[2] - bbox[0]), round(bbox[3] - bbox[1])


def _rebalance_wrapped_lines(
    lines: list[str], font: ImageFont.FreeTypeFont, max_width: int, stroke_width: float = 0
) -> list[str]:
    """
    Rebalance wrapped lines to avoid orphan lines/words.
    """
    if len(lines) < 2:
        return lines

    balanced = list(lines)
    for i in range(len(balanced) - 1):
        current_line = balanced[i]
        next_line = balanced[i + 1]

        while current_line and next_line:
            current_words = current_line.split()
            if len(current_words) <= 1:
                break

            current_width = _get_font_text_size(current_line, font, stroke_width=stroke_width)[0]
            next_width = _get_font_text_size(next_line, font, stroke_width=stroke_width)[0]

            if current_width == 0 or next_width / current_width >= 0.65:
                break

            moved_word = current_words.pop()
            candidate_current = " ".join(current_words)
            candidate_next = f"{moved_word} {next_line}".strip()

            if not candidate_current:
                break

            if _get_font_text_size(candidate_next, font, stroke_width=stroke_width)[0] > max_width:
                break

            new_current_width = _get_font_text_size(candidate_current, font, stroke_width=stroke_width)[0]
            new_next_width = _get_font_text_size(candidate_next, font, stroke_width=stroke_width)[0]

            if new_current_width and new_next_width / new_current_width > next_width / max(current_width, 1):
                current_line = candidate_current
                next_line = candidate_next
                balanced[i] = current_line
                balanced[i + 1] = next_line
            else:
                break

    if len(balanced) >= 2:
        last_words = balanced[-1].split()
        prev_words = balanced[-2].split()
        while len(last_words) < 2 and len(prev_words) > 1:
            candidate_next = " ".join([prev_words[-1], *last_words])
            candidate_prev = " ".join(prev_words[:-1])
            if not candidate_prev:
                break
            if _get_font_text_size(candidate_next, font, stroke_width=stroke_width)[0] > max_width:
                break
            balanced[-2] = candidate_prev
            balanced[-1] = candidate_next
            last_words = candidate_next.split()
            prev_words = candidate_prev.split()

    return balanced


def _draw_text_image(
    text: str,
    text_size: tuple[int, int],
    font: ImageFont.FreeTypeFont,
    line_height: int,
    font_color: tuple[int, int, int, float],
    align: str,
    stroke_color: str,
    stroke_width: float,
) -> Image.Image:
    """
    Create an image with the given text and font.
    """
    text_image = Image.new("RGBA", text_size, (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_image)

    # Draw main text
    text_draw.multiline_text(
        xy=(0, 0),
        text=text,
        font=font,
        fill=(font_color[0], font_color[1], font_color[2], round(font_color[3] * 255)),
        align=align,
        stroke_fill=stroke_color,
        stroke_width=round(stroke_width),
        spacing=line_height,
    )

    return text_image


def _draw_text_shadow_image(
    text: str,
    text_size: tuple[int, int],
    font: ImageFont.FreeTypeFont,
    line_height: int,
    align: str,
    shadow_color: str,
    shadow_angle: float,
    shadow_distance: float,
    shadow_blur: float,
    shadow_opacity: float,
) -> Image.Image:
    """
    Apply shadow to the text with angle and distance offset.
    """
    x_offset = round(shadow_distance * math.cos(math.radians(shadow_angle)))
    y_offset = round(shadow_distance * math.sin(math.radians(shadow_angle)))

    # Expand shadow image size to accommodate offset
    shadow_width = text_size[0] + abs(x_offset)
    shadow_height = text_size[1] + abs(y_offset)
    shadow_image = Image.new("RGBA", (shadow_width, shadow_height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_image)
    shadow_draw.multiline_text(
        (x_offset, y_offset),
        text,
        font=font,
        fill=shadow_color,
        spacing=line_height,
        align=align,
    )
    shadow_image = shadow_image.filter(ImageFilter.GaussianBlur(radius=shadow_blur))
    shadow_image = Image.blend(Image.new("RGBA", shadow_image.size, (0, 0, 0, 0)), shadow_image, shadow_opacity)
    return shadow_image
