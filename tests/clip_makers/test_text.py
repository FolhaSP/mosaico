import math

from PIL import ImageFont

from mosaico.assets.factory import create_asset
from mosaico.assets.text import TextAssetParams
from mosaico.clip_makers.factory import make_clip
from mosaico.clip_makers.text import (
    SystemFont,
    _draw_text_shadow_image,
    _get_font_text_size,
    _get_system_fallback_font_name,
    _list_system_fonts,
    _load_font,
    _slugify_font_name,
    _wrap_text,
)
from mosaico.positioning.region import RegionPosition
from mosaico.positioning.relative import RelativePosition


def test_system_font_properties():
    """Test SystemFont class properties."""
    font = SystemFont(path="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")

    assert font.name == "DejaVuSans-Bold"
    assert font.slug == "dejavusans-bold"
    assert font.matches("DejaVuSans-Bold")
    assert font.matches("dejavusans-bold")


def test_slugify_font_name():
    """Test font name slugification."""
    test_cases = [
        ("Arial Bold", "arial-bold"),
        ("Times_New_Roman", "times-new-roman"),
        ("Helvetica-Neue", "helvetica-neue"),
        ("Open Sans Regular", "open-sans-regular"),
        ("Font!!With@@Special##Chars", "fontwithspecialchars"),
    ]

    for input_name, expected_output in test_cases:
        assert _slugify_font_name(input_name) == expected_output


def test_list_system_fonts():
    """Test system fonts listing."""
    fonts = _list_system_fonts()

    assert isinstance(fonts, list)
    assert len(fonts) > 0
    assert all(isinstance(font, SystemFont) for font in fonts)


def test_load_font():
    """Test font loading."""
    # Test with default size
    font = _load_font(_get_system_fallback_font_name(), 12)
    assert isinstance(font, ImageFont.FreeTypeFont)

    # Test with non-existent font (should return default font)
    font = _load_font("NonExistentFont", 12)
    assert isinstance(font, ImageFont.FreeTypeFont)


def test_get_system_fallback_font():
    """Test system fallback font retrieval."""
    fallback_font = _get_system_fallback_font_name()
    assert isinstance(fallback_font, str)
    assert len(fallback_font) > 0


def test_wrap_text():
    """Test text wrapping functionality."""
    font = _load_font(_get_system_fallback_font_name(), 12)
    text = "This is a very long text that should be wrapped properly"

    wrapped = _wrap_text(text, font, 100)
    assert isinstance(wrapped, str)
    assert "\n" in wrapped


def test_text_size_calculation():
    """Test text size calculation."""
    font = _load_font(_get_system_fallback_font_name(), 12)
    text = "Test text"

    width, height = _get_font_text_size(text, font)
    assert isinstance(width, int)
    assert isinstance(height, int)
    assert width > 0
    assert height > 0


def test_font_matching():
    """Test font matching functionality."""
    font = SystemFont("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")

    assert font.matches("DejaVuSans-Bold")
    assert font.matches("dejavusans-bold")
    assert not font.matches("Arial")


def test_shadow_image_size_expansion():
    """Test that shadow image size is expanded to accommodate shadow offset."""
    font = _load_font(_get_system_fallback_font_name(), 40)
    text = "Test text"
    text_size = (50, 30)

    # Create shadow image with large offset
    shadow_image = _draw_text_shadow_image(
        text=text,
        text_size=text_size,
        font=font,
        line_height=0,
        align="left",
        shadow_color="black",
        shadow_angle=0,
        shadow_distance=40,  # Large offset
        shadow_blur=2,
        shadow_opacity=0.8,
    )

    # Shadow image should be expanded to accommodate the offset
    # With 40 pixel offset at 0 degrees, width should be 50 + 40 = 90
    assert shadow_image.size[0] == text_size[0] + 40  # 90
    assert shadow_image.size[1] == text_size[1]  # 30

    # Test with different angle
    shadow_image_diagonal = _draw_text_shadow_image(
        text=text,
        text_size=text_size,
        font=font,
        line_height=0,
        align="left",
        shadow_color="black",
        shadow_angle=45,  # 45 degree angle
        shadow_distance=30,
        shadow_blur=0,
        shadow_opacity=1.0,
    )

    # With 45 degree angle, both x and y offsets should be ~21 pixels
    # So both width and height should be expanded
    expected_offset = abs(round(30 * math.cos(math.radians(45))))
    assert shadow_image_diagonal.size[0] == text_size[0] + expected_offset
    assert shadow_image_diagonal.size[1] == text_size[1] + expected_offset


def test_user_scenario_with_negative_shadow_offset():
    """Test the exact scenario that caused the user's SystemError with negative shadow offset."""

    # Exact parameters from user's failing scenario
    text = "Los Angeles está sob toque de recolher enquanto protestos contra operações anti-imigração do presidente Trump se espalham por várias cidades americanas, com confrontos entre manifestantes e policiais."

    params = TextAssetParams(
        position=RegionPosition(x="center", y="bottom"),
        font_size=45,
        font_color="#fff",
        font_kerning=0,
        line_height=10,
        stroke_color="#000",
        stroke_width=1,
        shadow_color="#000",
        shadow_blur=10,
        shadow_opacity=0.5,
        shadow_angle=135,  # This creates negative x_offset
        shadow_distance=5,
        background_color="#0000",
        align="center",
        z_index=0,
    )

    # Create asset and make clip - this should work without SystemError
    asset = create_asset("text", data=text, params=params)
    resolution = (1920, 1080)
    duration = 16

    # This should not raise SystemError: tile cannot extend outside image
    clip = make_clip(asset, duration, resolution, effects=[])

    # Verify the clip was created successfully
    assert clip is not None
    assert clip.size[0] > 0
    assert clip.size[1] > 0


def test_empty_text_handling():
    """Test that empty text doesn't cause SystemError: tile cannot extend outside image."""

    # Create an empty text asset (this was causing the SystemError)
    params = TextAssetParams(
        position=RelativePosition(x=0.1, y=0.325),
        font_size=54,
        line_height=2,  # This was the specific combination causing issues
    )

    # Create asset with empty text
    asset = create_asset("text", data="", params=params)

    # This should not raise SystemError: tile cannot extend outside image
    resolution = (1920, 1080)
    duration = 5
    clip = make_clip(asset, duration, resolution, effects=[])

    # Verify the clip was created successfully with minimum dimensions
    assert clip is not None
    assert clip.size[0] >= 1  # Should have minimum width
    assert clip.size[1] >= 1  # Should have minimum height
