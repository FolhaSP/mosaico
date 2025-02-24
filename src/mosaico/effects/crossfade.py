from typing import Literal

from moviepy.video import fx as vfx
from moviepy.video.VideoClip import VideoClip

from mosaico.effects.fade import BaseFadeEffect


class CrossFadeInEffect(BaseFadeEffect):
    """fade-in effect for video clips."""

    type: Literal["crossfade_in"] = "crossfade_in"
    """Effect type. Must be "crossfade_in"."""

    def apply(self, clip: VideoClip) -> VideoClip:
        """
        Apply fade-in effect to clip.

        :param clip: The clip to apply the effect to.
        :return: The clip with the effect applied.
        """
        fx = vfx.CrossFadeIn(self.duration)
        return fx.apply(clip)  # type: ignore


class CrossFadeOutEffect(BaseFadeEffect):
    """fade-out effect for video clips."""

    type: Literal["crossfade_out"] = "crossfade_out"
    """Effect type. Must be "crossfade_out"."""

    def apply(self, clip: VideoClip) -> VideoClip:
        """
        Apply fade-out effect to clip.

        :param clip: The clip to apply the effect to.
        :return: The clip with the effect applied.
        """
        fx = vfx.CrossFadeOut(self.duration)
        return fx.apply(clip)  # type: ignore
