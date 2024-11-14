from abc import abstractmethod
from collections.abc import Callable
from typing import Literal

from moviepy.video.fx.resize import resize
from moviepy.video.VideoClip import VideoClip
from pydantic import BaseModel
from pydantic.types import PositiveFloat


PanFn = Callable[[float], tuple[float, str] | tuple[str, float]]
"""The pan function type."""


class BasePanEffect(BaseModel):
    """A pan effect."""

    zoom_factor: PositiveFloat = 1.1
    """The zoom factor."""

    @abstractmethod
    def _pan_fn(self, clip: VideoClip) -> PanFn:
        """
        Get the pan function.

        :param clip: The clip.
        :return: The pan function.
        """
        ...

    def apply(self, clip: VideoClip) -> VideoClip:
        """
        Apply the pan effect to the clip.

        :param clip: The clip.
        :return: The clip with the effect applied.
        """
        pan_fn = self._pan_fn(clip)
        return clip.fx(resize, self.zoom_factor).set_position(pan_fn)


class PanRightEffect(BasePanEffect):
    """A left to right pan effect."""

    type: Literal["pan_right"] = "pan_right"
    """Effect type. Must be "pan_right"."""

    def _pan_fn(self, clip: VideoClip) -> PanFn:
        def pan(t):
            x = (clip.w * self.zoom_factor - clip.w) * (t / clip.duration)
            return (-x, "center")

        return pan


class PanLeftEffect(BasePanEffect):
    """A right to left pan effect."""

    type: Literal["pan_left"] = "pan_left"
    """Effect type. Must be "pan_left"."""

    def _pan_fn(self, clip: VideoClip) -> PanFn:
        def pan(t):
            x = (clip.w * self.zoom_factor - clip.w) * (1 - t / clip.duration)
            return (-x, "center")

        return pan


class PanDownEffect(BasePanEffect):
    """A top to bottom pan effect."""

    type: Literal["pan_down"] = "pan_down"
    """Effect type. Must be "pan_down"."""

    def _pan_fn(self, clip: VideoClip) -> PanFn:
        def pan(t):
            y = (clip.h * self.zoom_factor - clip.h) * (t / clip.duration)
            return ("center", -y)

        return pan


class PanUpEffect(BasePanEffect):
    """A bottom to top pan effect."""

    type: Literal["pan_up"] = "pan_up"
    """Effect type. Must be "pan_up"."""

    def _pan_fn(self, clip: VideoClip) -> PanFn:
        def pan(t):
            y = (clip.h * self.zoom_factor - clip.h) * (1 - t / clip.duration)
            return ("center", -y)

        return pan
