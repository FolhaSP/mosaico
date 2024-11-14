from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from mosaico.assets.factory import create_asset


if TYPE_CHECKING:
    from mosaico.assets.types import Asset, AssetType
    from mosaico.media import Media


def convert_media_to_asset(media: Media) -> Asset:
    """
    Convert a media object to an asset.

    :param media: The media object to convert.
    :return: The asset object.
    :raises ValueError: If the media object does not have a MIME type or the MIME type is unsupported.
    """
    if media.mime_type is None:
        raise ValueError("Media object does not have a MIME type.")
    asset_type = guess_asset_type_from_mime_type(media.mime_type)
    return create_asset(asset_type, **media.model_dump())


def guess_asset_type_from_mime_type(mime_type: str) -> AssetType:
    """
    Guess the asset type from a MIME type.

    :param mime_type: The MIME type to guess the asset type from.
    :return: The asset type.
    """
    if mime_type.startswith("audio/"):
        return "audio"
    if mime_type.startswith("image/"):
        return "image"
    if mime_type.startswith("text/"):
        return "text"
    raise ValueError(f"Unsupported MIME type: {mime_type}")


def check_user_provided_required_keys(data: dict, required_keys: Sequence[str]) -> bool:
    """
    Check if the user provided all required keys.

    :param data: The data to check.
    :param required_keys: The required keys.
    :return: Whether the user provided all required keys.
    """
    return set(required_keys).issubset(data.keys())
