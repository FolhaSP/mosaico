import pytest

from mosaico.effects.crossfade import CrossFadeInEffect, CrossFadeOutEffect
from mosaico.effects.factory import EFFECT_MAP, create_effect
from mosaico.effects.fade import FadeInEffect, FadeOutEffect
from mosaico.effects.pan import PanDownEffect, PanLeftEffect, PanRightEffect, PanUpEffect
from mosaico.effects.zoom import ZoomInEffect, ZoomOutEffect


@pytest.mark.parametrize(
    "effect_type, expected_class",
    [
        ("pan_left", PanLeftEffect),
        ("pan_right", PanRightEffect),
        ("pan_up", PanUpEffect),
        ("pan_down", PanDownEffect),
        ("zoom_in", ZoomInEffect),
        ("zoom_out", ZoomOutEffect),
        ("fade_in", FadeInEffect),
        ("fade_out", FadeOutEffect),
        ("crossfade_in", CrossFadeInEffect),
        ("crossfade_out", CrossFadeOutEffect),
    ],
)
def test_create_effect_valid(effect_type, expected_class):
    effect = create_effect(effect_type)
    assert isinstance(effect, expected_class)


def test_create_effect_invalid():
    with pytest.raises(ValueError, match="Invalid effect type: invalid_effect"):
        create_effect("invalid_effect")


@pytest.mark.parametrize(
    "effect_type, params",
    [
        ("pan_left", {"zoom_factor": 1.2}),
        ("zoom_in", {"end_zoom": 1.6}),
    ],
)
def test_create_effect_with_params(effect_type, params):
    effect = create_effect(effect_type, **params)
    assert isinstance(effect, EFFECT_MAP[effect_type])
    for key, value in params.items():
        assert getattr(effect, key) == value
