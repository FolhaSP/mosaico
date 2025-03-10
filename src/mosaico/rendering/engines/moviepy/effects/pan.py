from __future__ import annotations

from moviepy.video import fx as vfx
from moviepy.video.VideoClip import VideoClip

from mosaico.effects.types import PanEffect
from mosaico.rendering.adapters.effect import EffectAdapter


class MoviepyPanEffectAdapter(EffectAdapter[VideoClip, PanEffect]):
    """A pan effect."""

    def apply(self, obj, effect):
        """
        Apply the pan effect to the clip.

        :param obj: The clip.
        :param effect: The effect.
        :return: The clip with the effect applied.
        """

        def _pan_right(t):
            x = (obj.w * effect.zoom_factor - obj.w) * (t / obj.duration)
            return (-x, "center")

        def _pan_left(t):
            x = (obj.w * effect.zoom_factor - obj.w) * (t / obj.duration)
            return (x, "center")

        def _pan_up(t):
            y = (obj.h * effect.zoom_factor - obj.h) * (1 - t / obj.duration)
            return ("center", -y)

        def _pan_down(t):
            y = (obj.h * effect.zoom_factor - obj.h) * (t / obj.duration)
            return ("center", -y)

        def _pan_center(t):
            x = (obj.w * effect.zoom_factor - obj.w) * (t / obj.duration)
            y = (obj.h * effect.zoom_factor - obj.h) * (1 - t / obj.duration)
            return (-x, -y)

        def pan_fn(t):
            if effect.type == "pan_right":
                return _pan_right(t)
            elif effect.type == "pan_left":
                return _pan_left(t)
            elif effect.type == "pan_up":
                return _pan_up(t)
            elif effect.type == "pan_down":
                return _pan_down(t)
            elif effect.type == "pan_center":
                return _pan_center(t)
            else:
                raise ValueError(f"Invalid effect type: {effect.type}")

        return obj.with_effects([vfx.Resize(effect.zoom_factor)]).with_position(pan_fn)  # type: ignore
