from __future__ import annotations

from typing import Literal, Union

from mosaico.positioning.absolute import AbsolutePosition
from mosaico.positioning.region import RegionPosition
from mosaico.positioning.relative import RelativePosition


PositionType = Literal["absolute", "relative", "region"]
"""An enumeration of the different types of positions that can be held in an assets."""

Position = Union[AbsolutePosition, RelativePosition, RegionPosition]
"""Represents a positioning of an assets in the frame."""
