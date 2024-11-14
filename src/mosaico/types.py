from __future__ import annotations

from pathlib import PurePath
from typing import Annotated

from pydantic.fields import Field


PathLike = str | PurePath
"""A type alias for paths."""

FrameSize = tuple[int, int]
"""A type alias for video resolutions."""

ModelTemperature = Annotated[float, Field(ge=0, le=1)]
"""A type alias for model temperatures."""
