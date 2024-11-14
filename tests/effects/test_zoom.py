import pytest
from moviepy.editor import ColorClip

from mosaico.effects.zoom import ZoomInEffect, ZoomOutEffect


@pytest.fixture
def sample_clip():
    # Create a sample video clip of 10 seconds duration
    return ColorClip(size=(640, 480), color=(255, 0, 0), duration=10)


def test_zoom_in_effect(sample_clip):
    zoom_in_effect = ZoomInEffect(start_zoom=1.0, end_zoom=1.5)
    result_clip = zoom_in_effect.apply(sample_clip)

    # Check if the effect is applied correctly at the start
    assert result_clip.get_frame(0).shape == (480, 640, 3)

    # Check if the effect is applied correctly at the end
    assert result_clip.get_frame(10).shape == (720, 960, 3)


def test_zoom_out_effect(sample_clip):
    zoom_out_effect = ZoomOutEffect(start_zoom=1.5, end_zoom=1.0)
    result_clip = zoom_out_effect.apply(sample_clip)

    # Check if the effect is applied correctly at the start
    assert result_clip.get_frame(0).shape == (720, 960, 3)

    # Check if the effect is applied correctly at the end
    assert result_clip.get_frame(10).shape == (480, 640, 3)


def test_invalid_zoom_in_effect():
    with pytest.raises(ValueError, match="For zoom-in, start_zoom must be less than end_zoom"):
        ZoomInEffect(start_zoom=1.5, end_zoom=1.0)


def test_invalid_zoom_out_effect():
    with pytest.raises(ValueError, match="For zoom-out, start_zoom must be greater than end_zoom"):
        ZoomOutEffect(start_zoom=1.0, end_zoom=1.5)
