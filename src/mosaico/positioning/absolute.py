from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel
from pydantic.config import ConfigDict
from pydantic.types import NonNegativeInt

from mosaico.types import FrameSize


if TYPE_CHECKING:
    from mosaico.positioning.region import RegionPosition
    from mosaico.positioning.relative import RelativePosition


class AbsolutePosition(BaseModel):
    """Represents an absolute positioning."""

    type: Literal["absolute"] = "absolute"
    """The type of positioning. Defaults to "absolute"."""

    x: NonNegativeInt = 0
    """The x-coordinate of the assets."""

    y: NonNegativeInt = 0
    """The y-coordinate of the assets."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    @classmethod
    def from_relative(cls, position: RelativePosition, frame_size: FrameSize) -> AbsolutePosition:
        """
        Creates an absolute positioning from a relative positioning.

        :param position: The relative positioning.
        :param frame_size: The size of the frame.
        :return: The absolute positioning.
        """
        frame_max_width, frame_max_height = frame_size
        return cls(x=int(position.x * frame_max_width), y=int(position.y * frame_max_height))

    @classmethod
    def from_region(cls, position: RegionPosition, frame_size: FrameSize) -> AbsolutePosition:
        """
        Creates an absolute positioning from a region positioning.

        :param position: The region positioning.
        :param frame_max_width: The maximum width of the frame.
        :param frame_max_height: The maximum height of the frame.
        :return: The absolute positioning.
        """
        frame_max_width, frame_max_height = frame_size
        x_map = {"left": 0, "center": frame_max_width // 2, "right": frame_max_width}
        y_map = {"top": 0, "center": frame_max_height // 2, "bottom": frame_max_height}
        return cls(x=x_map[position.x], y=y_map[position.y])
