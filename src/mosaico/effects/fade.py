from typing import Literal

from pydantic.types import PositiveFloat

from mosaico.effects.base import BaseEffect


class BaseFadeEffect(BaseEffect):
    """Base class for fade effects."""

    duration: PositiveFloat = 1
    """Duration of the fade effect, in seconds."""


class FadeInEffect(BaseFadeEffect):
    """Fade-in effect for video clips."""

    type: Literal["fade_in"] = "fade_in"
    """Type of the effect."""


class FadeOutEffect(BaseFadeEffect):
    """Fade-out effect for video clips."""

    type: Literal["fade_out"] = "fade_out"
    """Type of the effect."""


class CrossFadeInEffect(BaseFadeEffect):
    """Cross-fade-in effect for video clips."""

    type: Literal["cross_fade_in"] = "cross_fade_in"
    """Type of the effect."""


class CrossFadeOutEffect(BaseFadeEffect):
    """Cross-fade-out effect for video clips."""

    type: Literal["cross_fade_out"] = "cross_fade_out"
    """Type of the effect."""
