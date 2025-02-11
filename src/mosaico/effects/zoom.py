from typing import Annotated, Literal

from moviepy.video import fx as vfx
from moviepy.video.VideoClip import VideoClip
from pydantic import BaseModel
from pydantic.fields import Field
from pydantic.functional_validators import model_validator
from typing_extensions import Self


class BaseZoomEffect(BaseModel):
    """Base class for zoom effects."""

    start_zoom: Annotated[float, Field(ge=0.1, le=2)]
    """Starting zoom scale (1.0 is original size)."""

    end_zoom: Annotated[float, Field(ge=0.1, le=2.0)]
    """Ending zoom scale."""

    def apply(self, clip: VideoClip) -> VideoClip:
        """
        Apply zoom effect to clip.

        :param clip: The clip to apply the effect to.
        :return: The clip with the effect applied.
        """

        def zoom(t):
            """Calculate zoom factor at time t."""
            progress = t / clip.duration
            return self.start_zoom + (self.end_zoom - self.start_zoom) * progress

        return clip.with_effects([vfx.Resize(zoom)])  # type: ignore


class ZoomInEffect(BaseZoomEffect):
    """Zoom-in effect for video clips."""

    type: Literal["zoom_in"] = "zoom_in"
    """Effect type. Must be "zoom_in"."""

    start_zoom: Annotated[float, Field(ge=0.1, le=2)] = 1.0
    """Starting zoom scale (1.0 is original size)."""

    end_zoom: Annotated[float, Field(ge=0.1, le=2)] = 1.1
    """Ending zoom scale."""

    @model_validator(mode="after")
    def _validate_zoom_in(self) -> Self:
        if self.start_zoom >= self.end_zoom:
            raise ValueError("For zoom-in, start_zoom must be less than end_zoom")
        return self


class ZoomOutEffect(BaseZoomEffect):
    """Zoom-out effect for video clips."""

    type: Literal["zoom_out"] = "zoom_out"
    """Effect type. Must be "zoom_out"."""

    start_zoom: Annotated[float, Field(ge=0.1, le=2)] = 1.5
    """Starting zoom scale (1.5 times the original size)."""

    end_zoom: Annotated[float, Field(ge=0.1, le=2)] = 1.4
    """Ending zoom scale."""

    @model_validator(mode="after")
    def _validate_zoom_out(self) -> Self:
        if self.start_zoom <= self.end_zoom:
            raise ValueError("For zoom-out, start_zoom must be greater than end_zoom")
        return self
