from typing import Literal

from moviepy.video import fx as vfx
from moviepy.video.VideoClip import VideoClip
from pydantic import BaseModel
from pydantic.types import PositiveFloat


class BaseFadeEffect(BaseModel):
    """Base class for fade effects."""

    duration: PositiveFloat = 1
    """Duration of the fade effect, in seconds."""


class FadeInEffect(BaseFadeEffect):
    """fade-in effect for video clips."""

    type: Literal["fade_in"] = "fade_in"
    """Effect type. Must be "fade_in"."""

    def apply(self, clip: VideoClip) -> VideoClip:
        """
        Apply fade-in effect to clip.

        :param clip: The clip to apply the effect to.
        :return: The clip with the effect applied.
        """
        fx = vfx.FadeIn(self.duration)
        return fx.apply(clip)  # type: ignore


class FadeOutEffect(BaseFadeEffect):
    """fade-out effect for video clips."""

    type: Literal["fade_out"] = "fade_out"
    """Effect type. Must be "fade_out"."""

    def apply(self, clip: VideoClip) -> VideoClip:
        """
        Apply fade-out effect to clip.

        :param clip: The clip to apply the effect to.
        :return: The clip with the effect applied.
        """
        fx = vfx.FadeOut(self.duration)
        return fx.apply(clip)  # type: ignore
