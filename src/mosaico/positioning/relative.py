from __future__ import annotations

from typing import Literal

from pydantic import BaseModel
from pydantic.config import ConfigDict
from pydantic.types import NonNegativeFloat


class RelativePosition(BaseModel):
    """Represents a relative position."""

    type: Literal["relative"] = "relative"
    """The type of position. Defaults to "relative"."""

    x: NonNegativeFloat = 0.5
    """The x-coordinate of the assets."""

    y: NonNegativeFloat = 0.5
    """The y-coordinate of the assets."""

    model_config = ConfigDict(frozen=True, extra="forbid")
