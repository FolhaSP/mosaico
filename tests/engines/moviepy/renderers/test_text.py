from PIL import ImageFont

from mosaico.rendering.engines.moviepy.renderers.text import (
    SystemFont,
    _get_font_text_size,
    _get_system_fallback_font_name,
    _list_system_fonts,
    _load_font,
    _slugify_font_name,
    _wrap_text,
)


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
