from __future__ import annotations

import io
from typing import Literal

from PIL import Image
from pydantic import BaseModel
from pydantic.config import ConfigDict
from pydantic.fields import Field
from pydantic.types import NonNegativeInt

from mosaico.assets.base import BaseAsset
from mosaico.positioning import AbsolutePosition, Position
from mosaico.types import FrameSize


class ImageInfo(BaseModel):
    """Represents an image metadata information."""

    width: NonNegativeInt
    """The width of the image, in pixels."""

    height: NonNegativeInt
    """The height of the image, in pixels."""

    mode: str
    """Image mode."""


class ImageAssetParams(BaseModel):
    """Represents the parameters for an image assets."""

    position: Position = Field(default_factory=AbsolutePosition)
    """The positioning of the text assets in the video."""

    z_index: int = -1
    """The z-index of the assets."""

    crop: tuple[int, int, int, int] | None = None
    """The crop range for the image assets."""

    as_background: bool = True
    """Whether the image should be used as a background."""

    model_config = ConfigDict(validate_assignment=True)


class ImageAsset(BaseAsset[ImageAssetParams, ImageInfo]):
    """Represents an image assets with various properties."""

    type: Literal["image"] = "image"  # type: ignore
    """The type of the assets. Defaults to "image"."""

    params: ImageAssetParams = Field(default_factory=ImageAssetParams)
    """The parameters for the assets."""

    @property
    def width(self) -> int:
        """
        The width of the image, in pixels.

        Wrapper of `ImageAsset.info.width` for convenience and type-hint compatibility.
        """
        return self._safe_get_info_key("width")

    @property
    def height(self) -> int:
        """
        The height of the image, in pixels.

        Wrapper of `ImageAsset.info.height` for convenience and type-hint compatibility.
        """
        return self._safe_get_info_key("height")

    @property
    def mode(self) -> str:
        """
        Image mode.

        Wrapper of `ImageAsset.info.mode` for convenience and type-hint compatibility.
        """
        return self._safe_get_info_key("mode")

    @property
    def size(self) -> FrameSize:
        """
        Image dimensions as a tuple.
        """
        return self.width, self.height

    def _load_info(self) -> None:
        if self.info is not None:
            return

        if self.data is not None:
            data = self.data
            if isinstance(data, str):
                data = data.encode("utf-8")
        else:
            data = self.to_bytes()
            self.data = data

        with Image.open(io.BytesIO(data)) as img:
            width, height = img.size
            self.info = ImageInfo(width=width, height=height, mode=img.mode)
