from __future__ import annotations

import math
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import cast

from find_system_fonts_filename import get_system_fonts_filename
from find_system_fonts_filename.exceptions import FindSystemFontsFilenameException
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
        max_width, max_height = self.video_resolution

        # Load the font and wrap the text
        font = _load_font(params.font_family, params.font_size)
        text = asset.to_string(storage_options=self.storage_options)
        wrapped_text = _wrap_text(text, font, round(max_width * 0.9))
        text_size = _get_font_text_size(wrapped_text, font)

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
            final_image = Image.alpha_composite(shadow_image, text_image)
        else:
            final_image = text_image.copy()

        bbox = final_image.getbbox()
        final_image = final_image.crop(bbox)

        with NamedTemporaryFile(suffix=".png") as f:
            final_image.save(f.name, "PNG")

            return (
                ImageClip(f.name)
                .set_position((params.position.x, params.position.y), relative=is_relative_position(params.position))
                .set_duration(self.duration)
            )


def _load_font(font_family: str, font_size: int) -> ImageFont.FreeTypeFont:
    """
    Load the font with the given family and size.
    """
    available_fonts = {Path(file).with_suffix("").name: file for file in get_system_fonts_filename()}
    if font_family not in available_fonts:
        raise FindSystemFontsFilenameException(f"Font {font_family} not found in system fonts")
    return ImageFont.truetype(font=available_fonts[font_family], size=font_size)


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
    """
    Wrap the given text to fit within the given width.
    """
    lines = []
    for line in text.split("\n"):
        if _get_font_text_size(line, font)[0] <= max_width:
            lines.append(line)
        else:
            words = line.split()
            wrapped_line = ""
            for word in words:
                test_line = wrapped_line + word + " "
                if _get_font_text_size(test_line, font)[0] <= max_width:
                    wrapped_line = test_line
                else:
                    lines.append(wrapped_line)
                    wrapped_line = word + " "
            lines.append(wrapped_line)
    return "\n".join(lines)


def _get_font_text_size(text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    """
    Get the width and height of the text with the given font.
    """
    left, top, right, bottom = font.getbbox(text)
    text_width = round(right - left)
    text_height = round(bottom - top)
    return text_width, text_height * text.count("\n") + 2 * text_height


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

    shadow_image = Image.new("RGBA", text_size, (0, 0, 0, 0))
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
