from typing import Literal

from mosaico.effects.fade import FadeInEffect, FadeOutEffect
from mosaico.effects.pan import PanDownEffect, PanLeftEffect, PanRightEffect, PanUpEffect
from mosaico.effects.zoom import ZoomInEffect, ZoomOutEffect


VideoEffect = (
    ZoomInEffect
    | ZoomOutEffect
    | PanLeftEffect
    | PanRightEffect
    | PanUpEffect
    | PanDownEffect
    | FadeInEffect
    | FadeOutEffect
)
"""A type representing any video effect."""

VideoEffectType = Literal["zoom_in", "zoom_out", "pan_left", "pan_right", "pan_up", "pan_down", "fade_in", "fade_out"]
"""A type representing the type of a video effect."""
