import pytest

from mosaico.effects.fade import FadeInEffect, FadeOutEffect


class DummyClip:
    duration = 10

    def time_transform(self, transform_fn):
        self._transform_fn = transform_fn
        return self

    def get_transformed_value(self, t):
        return self._transform_fn(t)


@pytest.fixture
def dummy_clip():
    return DummyClip()


def test_fade_in_effect(dummy_clip):
    # Create a valid FadeInEffect
    effect = FadeInEffect(start_fade=0.0, end_fade=1.0)
    result_clip = effect.apply(dummy_clip)

    # Test interpolation: expected fade = start + (end - start) * (t / duration)
    assert result_clip.get_transformed_value(0) == pytest.approx(0.0)
    assert result_clip.get_transformed_value(5) == pytest.approx(0.5)
    assert result_clip.get_transformed_value(10) == pytest.approx(1.0)


def test_fade_out_effect(dummy_clip):
    # Create a valid FadeOutEffect
    effect = FadeOutEffect(start_fade=1.0, end_fade=0.0)
    result_clip = effect.apply(dummy_clip)

    # Test interpolation: expected fade = start + (end - start) * (t / duration)
    assert result_clip.get_transformed_value(0) == pytest.approx(1.0)
    assert result_clip.get_transformed_value(5) == pytest.approx(0.5)
    assert result_clip.get_transformed_value(10) == pytest.approx(0.0)


def test_fade_in_effect_invalid():
    # For fade in, start_fade must be < end_fade.
    with pytest.raises(ValueError):
        FadeInEffect(start_fade=0.7, end_fade=0.5)


def test_fade_out_effect_invalid():
    # For fade out, start_fade must be > end_fade.
    with pytest.raises(ValueError):
        FadeOutEffect(start_fade=0.3, end_fade=0.7)
