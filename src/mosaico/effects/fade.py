from typing import Annotated, Literal

from moviepy.video.VideoClip import VideoClip
from pydantic import BaseModel
from pydantic.fields import Field
from pydantic.functional_validators import model_validator
from typing_extensions import Self


class BaseFadeEffect(BaseModel):
    """Base class for fade effects."""

    start_fade: Annotated[float, Field(ge=0, le=1.0)]
    """Starting fade scale (1.0 is original opacity)."""

    end_fade: Annotated[float, Field(ge=0, le=1.0)]
    """Ending fade scale."""

    def apply(self, clip: VideoClip) -> VideoClip:
        """
        Apply fade effect to clip.

        :param clip: The clip to apply the effect to.
        :return: The clip with the effect applied.
        """

        def fade(t):
            """Calculate fade factor at time t."""
            progress = t / clip.duration
            return self.start_fade + (self.end_fade - self.start_fade) * progress

        return clip.fl(fade)


class FadeInEffect(BaseFadeEffect):
    """fade-in effect for video clips."""

    type: Literal["fade_in"] = "fade_in"
    """Effect type. Must be "fade_in"."""

    start_fade: Annotated[float, Field(ge=0, le=1)] = 0
    """Starting fade from invisible object."""

    end_fade: Annotated[float, Field(ge=0, le=1)] = 1.0
    """Ending fade scale."""

    @model_validator(mode="after")
    def _validate_fade_in(self) -> Self:
        if self.start_fade >= self.end_fade:
            raise ValueError("For fade-in, start_fade must be less than end_fade")
        return self


class FadeOutEffect(BaseFadeEffect):
    """fade-out effect for video clips."""

    type: Literal["fade_out"] = "fade_out"
    """Effect type. Must be "fade_out"."""

    start_fade: Annotated[float, Field(ge=0, le=1)] = 1.0
    """Starting fade scale (1.5 times the original size)."""

    end_fade: Annotated[float, Field(ge=0, le=1)] = 0
    """Ending fade scale."""

    @model_validator(mode="after")
    def _validate_fade_out(self) -> Self:
        if self.start_fade <= self.end_fade:
            raise ValueError("For fade-out, start_fade must be greater than end_fade")
        return self
