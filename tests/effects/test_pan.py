import pytest
from moviepy.editor import ColorClip

from mosaico.effects.pan import PanDownEffect, PanLeftEffect, PanRightEffect, PanUpEffect


@pytest.fixture
def video_clip() -> ColorClip:
    return ColorClip(size=(640, 480), color=(255, 0, 0), duration=10)


def test_pan_right_effect(video_clip: ColorClip) -> None:
    zoom_factor = 1.2
    effect = PanRightEffect(zoom_factor=zoom_factor)
    result_clip = effect.apply(video_clip)
    assert result_clip.size == (640 * zoom_factor, 480 * zoom_factor)
    assert result_clip.duration == 10

    # Test the pan function
    pan_fn = effect._pan_fn(video_clip)
    assert pan_fn(0) == (0, "center")
    assert pan_fn(5) == (-64, "center")
    assert pan_fn(10) == (-128, "center")


def test_pan_left_effect(video_clip: ColorClip) -> None:
    zoom_factor = 1.2
    effect = PanLeftEffect(zoom_factor=zoom_factor)
    result_clip = effect.apply(video_clip)
    assert result_clip.size == (640 * zoom_factor, 480 * zoom_factor)
    assert result_clip.duration == 10

    # Test the pan function
    pan_fn = effect._pan_fn(video_clip)
    assert pan_fn(0) == (-128, "center")
    assert pan_fn(5) == (-64, "center")
    assert pan_fn(10) == (0, "center")


def test_pan_down_effect(video_clip: ColorClip) -> None:
    zoom_factor = 1.2
    effect = PanDownEffect(zoom_factor=zoom_factor)
    result_clip = effect.apply(video_clip)
    assert result_clip.size == (640 * zoom_factor, 480 * zoom_factor)
    assert result_clip.duration == 10

    # Test the pan function
    pan_fn = effect._pan_fn(video_clip)
    assert pan_fn(0) == ("center", 0)
    assert pan_fn(5) == ("center", -48)
    assert pan_fn(10) == ("center", -96)


def test_pan_up_effect(video_clip: ColorClip) -> None:
    zoom_factor = 1.2
    effect = PanUpEffect(zoom_factor=zoom_factor)
    result_clip = effect.apply(video_clip)
    assert result_clip.size == (640 * zoom_factor, 480 * zoom_factor)
    assert result_clip.duration == 10

    # Test the pan function
    pan_fn = effect._pan_fn(video_clip)
    assert pan_fn(0) == ("center", -96)
    assert pan_fn(5) == ("center", -48)
    assert pan_fn(10) == ("center", 0)
