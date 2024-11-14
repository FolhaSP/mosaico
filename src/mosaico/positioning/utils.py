from __future__ import annotations

from typing import TYPE_CHECKING

from mosaico.positioning.absolute import AbsolutePosition
from mosaico.positioning.region import RegionPosition
from mosaico.positioning.relative import RelativePosition


if TYPE_CHECKING:
    from mosaico.positioning.types import Position
    from mosaico.types import FrameSize


def convert_position_to_absolute(position: Position, frame_size: FrameSize) -> AbsolutePosition:
    """
    Convert a relative position to an absolute position.

    :param position: The position to be converted.
    :param frame_size: The size of the frame.
    :return: The converted absolute positioning object.
    """
    if isinstance(position, AbsolutePosition):
        return position

    if isinstance(position, RelativePosition):
        return AbsolutePosition.from_relative(position, frame_size)

    return AbsolutePosition.from_region(position, frame_size)


def is_region_position(position: Position) -> bool:
    """
    Check if the position is a region position.

    :param position: The position to be checked.
    :return: Whether the position is a region position.
    """
    return isinstance(position, RegionPosition)


def is_relative_position(position: Position) -> bool:
    """
    Check if the position is a relative position.

    :param position: The position to be checked.
    :return: Whether the position is a relative position.
    """
    return isinstance(position, RelativePosition)


def is_absolute_position(position: Position) -> bool:
    """
    Check if the position is an absolute position.

    :param position: The position to be checked.
    :return: Whether the position is an absolute position.
    """
    return isinstance(position, AbsolutePosition)
