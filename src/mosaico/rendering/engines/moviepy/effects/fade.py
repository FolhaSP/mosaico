from __future__ import annotations

from typing import cast

from moviepy.video import fx as vfx
from moviepy.video.VideoClip import VideoClip

from mosaico.effects.types import CrossFadeEffect, FadeEffect
from mosaico.rendering.adapters.effect import EffectAdapter


class MoviepyFadeEffectAdapter(EffectAdapter[VideoClip, FadeEffect]):
    """
    Adapter for applying fade effects using MoviePy.
    """

    def apply(self, obj, effect):
        """
        Apply fade-in effect to clip.

        :param clip: The clip to apply the effect to.
        :return: The clip with the effect applied.
        """
        fx = vfx.FadeIn(effect.duration) if effect.type == "fade_in" else vfx.FadeOut(effect.duration)
        return cast(VideoClip, fx.apply(obj))


class MoviepyCrossFadeEffectAdapter(EffectAdapter[VideoClip, CrossFadeEffect]):
    """
    Adapter for applying cross-fade-out effect using MoviePy.
    """

    def apply(self, obj, effect):
        """
        Apply cross-fade-out effect to clip.

        :param clip: The clip to apply the effect to.
        :return: The clip with the effect applied.
        """
        fx = vfx.CrossFadeIn(effect.duration) if effect.type == "cross_fade_in" else vfx.CrossFadeOut(effect.duration)
        return cast(VideoClip, fx.apply(obj))
