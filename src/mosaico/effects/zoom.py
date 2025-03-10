from typing import Annotated, Literal

from pydantic.fields import Field
from pydantic.functional_validators import model_validator
from typing_extensions import Self

from mosaico.effects.base import BaseEffect


class BaseZoomEffect(BaseEffect):
    """Base class for zoom effects."""

    start_zoom: Annotated[float, Field(ge=0.1, le=2)]
    """Starting zoom scale (1.0 is original size)."""

    end_zoom: Annotated[float, Field(ge=0.1, le=2.0)]
    """Ending zoom scale."""


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
