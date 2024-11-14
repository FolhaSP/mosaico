from __future__ import annotations

from typing import Literal, cast

from pydantic import BaseModel
from pydantic.config import ConfigDict


RegionX = Literal["left", "center", "right"]
"""The possible region x-coordinates of the assets."""

RegionY = Literal["top", "center", "bottom"]
"""The possible region y-coordinates of the assets."""


class RegionPosition(BaseModel):
    """Represents a region positioning."""

    type: Literal["region"] = "region"
    """The type of positioning. Defaults to "region"."""

    x: RegionX = "center"
    """The region x-coordinate of the assets."""

    y: RegionY = "center"
    """The region y-coordinate of the assets."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    @classmethod
    def from_string(cls, string: str) -> RegionPosition:
        """
        Create a region position from a string.

        :param string: The string to parse.
        :return: The region position.
        """
        if string not in {"left", "center", "right", "top", "center", "bottom"}:
            raise ValueError("Invalid region position")
        if string in {"left", "center", "right"}:
            return cls(x=cast(RegionX, string), y="center")
        if string in {"top", "bottom"}:
            return cls(x="center", y=cast(RegionY, string))
        raise ValueError("Invalid region position")
