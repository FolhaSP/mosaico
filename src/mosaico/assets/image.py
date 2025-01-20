from __future__ import annotations

import io
from typing import Any, Literal

from PIL import Image
from pydantic import BaseModel
from pydantic.config import ConfigDict
from pydantic.fields import Field
from pydantic.types import NonNegativeInt
from typing_extensions import Self

from mosaico.assets.base import BaseAsset
from mosaico.assets.utils import check_user_provided_required_keys
from mosaico.media import _load_file
from mosaico.positioning import AbsolutePosition, Position
from mosaico.types import FilePath


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


class ImageAsset(BaseAsset[ImageAssetParams]):
    """Represents an image assets with various properties."""

    type: Literal["image"] = "image"
    """The type of the assets. Defaults to "image"."""

    params: ImageAssetParams = Field(default_factory=ImageAssetParams)
    """The parameters for the assets."""

    width: NonNegativeInt
    """The width of the image."""

    height: NonNegativeInt
    """The height of the image."""

    @classmethod
    def from_data(
        cls,
        data: str | bytes,
        *,
        path: FilePath | None = None,
        metadata: dict | None = None,
        mime_type: str | None = None,
        **kwargs: Any,
    ) -> Self:
        """
        Creates an image asset from data.

        :param data: The data of the assets.
        :param path: The path to the file.
        :param metadata: The metadata of the assets.
        :param mime_type: The MIME type of the assets.
        :param kwargs: Additional keyword arguments to the constructor.
        :return: The assets.
        """
        if not check_user_provided_required_keys(kwargs, ["width", "height"]):
            if isinstance(data, str):
                data = data.encode("utf-8")

            with Image.open(io.BytesIO(data)) as img:
                kwargs["width"], kwargs["height"] = img.size

        return super().from_data(data, path=path, metadata=metadata, mime_type=mime_type, **kwargs)

    @classmethod
    def from_path(
        cls,
        path: FilePath,
        *,
        encoding: str = "utf-8",
        mime_type: str | None = None,
        guess_mime_type: bool = True,
        metadata: dict | None = None,
        **kwargs: Any,
    ) -> Self:
        """
        Creates an image asset from a file path.

        :param path: The path to the file.
        :param encoding: The encoding of the file.
        :param metadata: The metadata of the assets.
        :param mime_type: The MIME type of the assets.
        :param guess_mime_type: Whether to guess the MIME type.
        :param kwargs: Additional keyword arguments to the constructor.
        :return: The assets.
        """
        storage_options = kwargs.pop("storage_options", None)

        if not check_user_provided_required_keys(kwargs, ["width", "height"]):
            raw_image = _load_file(path, storage_options)
            with Image.open(io.BytesIO(raw_image)) as image:
                kwargs["width"], kwargs["height"] = image.size

        return super().from_path(
            path, encoding=encoding, mime_type=mime_type, guess_mime_type=guess_mime_type, metadata=metadata, **kwargs
        )
