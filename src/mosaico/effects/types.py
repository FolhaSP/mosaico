from __future__ import annotations

from typing import Literal

from mosaico.effects.fade import CrossFadeInEffect, CrossFadeOutEffect, FadeInEffect, FadeOutEffect
from mosaico.effects.pan import PanCenterEffect, PanDownEffect, PanLeftEffect, PanRightEffect, PanUpEffect
from mosaico.effects.zoom import ZoomInEffect, ZoomOutEffect


VideoEffect = (
    CrossFadeInEffect
    | CrossFadeOutEffect
    | FadeInEffect
    | FadeOutEffect
    | PanCenterEffect
    | PanDownEffect
    | PanLeftEffect
    | PanRightEffect
    | PanUpEffect
    | ZoomInEffect
    | ZoomOutEffect
)
"""A type representing any video effect."""

FadeEffect = FadeInEffect | FadeOutEffect
"""Type of the fade effect."""

CrossFadeEffect = CrossFadeInEffect | CrossFadeOutEffect
"""Type of the cross-fade effect."""

PanEffect = PanLeftEffect | PanRightEffect | PanUpEffect | PanDownEffect | PanCenterEffect
"""Type of the pan effect."""

ZoomEffect = ZoomInEffect | ZoomOutEffect
"""Type of the zoom effect."""

EffectType = Literal[
    "cross_fade_in",
    "cross_fade_out",
    "fade_in",
    "fade_out",
    "pan_center",
    "pan_down",
    "pan_left",
    "pan_right",
    "pan_up",
    "zoom_in",
    "zoom_out",
]
"""A type representing the type of a video effect."""
