from typing import cast

from moviepy.video import fx as vfx
from moviepy.video.VideoClip import VideoClip

from mosaico.effects.types import ZoomEffect
from mosaico.rendering.adapters.effect import EffectAdapter


class MoviepyZoomEffectAdapter(EffectAdapter[VideoClip, ZoomEffect]):
    """Base class for zoom effects."""

    def apply(self, obj, effect):
        """
        Apply zoom effect to clip.

        :param clip: The clip to apply the effect to.
        :return: The clip with the effect applied.
        """

        def zoom(t):
            """Calculate zoom factor at time t."""
            progress = t / obj.duration
            return effect.start_zoom + (effect.end_zoom - effect.start_zoom) * progress

        return cast(VideoClip, obj.with_effects([vfx.Resize(zoom)]))
