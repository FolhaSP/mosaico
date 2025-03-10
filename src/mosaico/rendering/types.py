from typing import Literal

from pydantic import BaseModel
from pydantic.types import PositiveInt

from mosaico.types import FrameSize


class RenderingOptions(BaseModel):
    """The options for rendering a video."""

    resolution: FrameSize = (1920, 1080)
    """The resolution of the project in pixels. Defaults to 1920x1080."""

    fps: PositiveInt = 30
    """The frames per second of the project. Defaults to 30."""

    engine: Literal["moviepy"] = "moviepy"
    """
    The rendering engine to use. Defaults to 'moviepy'.

    Currently supported engines:
        - moviepy: Uses the MoviePy library for rendering.
    """
