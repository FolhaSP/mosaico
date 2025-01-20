from __future__ import annotations

import importlib
import importlib.util
from typing import TYPE_CHECKING, Any, Literal, overload

from mosaico.exceptions import InvalidAssetTypeError


if TYPE_CHECKING:
    from mosaico.assets.audio import AudioAsset, AudioAssetParams
    from mosaico.assets.image import ImageAsset, ImageAssetParams
    from mosaico.assets.subtitle import SubtitleAsset
    from mosaico.assets.text import TextAsset, TextAssetParams
    from mosaico.assets.types import Asset, AssetParams, AssetType
    from mosaico.types import FilePath


@overload
def create_asset(
    asset_type: Literal["image"],
    id: str | None = ...,
    data: str | bytes | None = ...,
    path: FilePath | None = ...,
    metadata: dict[str, Any] | None = ...,
    params: ImageAssetParams | None = ...,
    **kwargs: Any,
) -> ImageAsset: ...


@overload
def create_asset(
    asset_type: Literal["audio"],
    id: str | None = ...,
    data: str | bytes | None = ...,
    path: FilePath | None = ...,
    metadata: dict[str, Any] | None = ...,
    params: AudioAssetParams | None = ...,
    **kwargs: Any,
) -> AudioAsset: ...


@overload
def create_asset(
    asset_type: Literal["text"],
    id: str | None = ...,
    data: str | bytes | None = ...,
    path: FilePath | None = ...,
    metadata: dict[str, Any] | None = ...,
    params: TextAssetParams | None = ...,
    **kwargs: Any,
) -> TextAsset: ...


@overload
def create_asset(
    asset_type: Literal["subtitle"],
    id: str | None = ...,
    data: str | bytes | None = ...,
    path: FilePath | None = ...,
    metadata: dict[str, Any] | None = ...,
    params: TextAssetParams | None = ...,
    **kwargs: Any,
) -> SubtitleAsset: ...


@overload
def create_asset(
    asset_type: AssetType,
    id: str | None = ...,
    data: str | bytes | None = ...,
    path: FilePath | None = ...,
    metadata: dict[str, Any] | None = ...,
    params: AssetParams | None = ...,
    **kwargs: Any,
) -> Asset: ...


def create_asset(
    asset_type: AssetType,
    id: str | None = None,
    data: str | bytes | None = None,
    path: FilePath | None = None,
    metadata: dict[str, Any] | None = None,
    params: AssetParams | dict[str, Any] | None = None,
    **kwargs: Any,
) -> Asset:
    """
    Create an asset from the given asset type.

    :param asset_type: The asset type.
    :param id: The asset ID.
    :param data: The asset data.
    :param path: The asset path.
    :param metadata: The asset metadata.
    ;param params: The asset parameters.
    :param kwargs: Additional keyword arguments.
    :return: The asset.
    """
    asset_mod_name = f"mosaico.assets.{asset_type}"

    if not importlib.util.find_spec(asset_mod_name):
        raise InvalidAssetTypeError(asset_type)

    asset_mod = importlib.import_module(f"mosaico.assets.{asset_type}")
    asset_class = getattr(asset_mod, asset_type.capitalize() + "Asset")

    def _get_asset_class_default_params(asset_class: type[Asset]) -> AssetParams:
        params_field = asset_class.model_fields["params"]
        params_factory = params_field.default_factory
        if params_factory is None:
            raise ValueError(f"Asset class '{asset_class.__name__}' does not have a default params factory.")
        return params_factory()

    def _merge_params_with_dict(params: AssetParams, params_dict: dict[str, Any]) -> AssetParams:
        new_params = params.__class__.model_validate(params_dict)
        for field_name in new_params.model_fields_set:
            setattr(params, field_name, getattr(new_params, field_name))
        return params

    if params is not None:
        if isinstance(params, dict):
            default_params = _get_asset_class_default_params(asset_class)
            params = _merge_params_with_dict(default_params, params)

        kwargs["params"] = params

    if data is not None:
        return asset_class.from_data(data, id=id, path=path, metadata=metadata, **kwargs)

    if path is None:
        msg = "Either 'data' or 'path' must be provided."
        raise ValueError(msg)

    return asset_class.from_path(path, id=id, metadata=metadata, **kwargs)


@overload
def get_asset_params_class(asset_type: Literal["image"]) -> type[ImageAssetParams]: ...


@overload
def get_asset_params_class(asset_type: Literal["audio"]) -> type[AudioAssetParams]: ...


@overload
def get_asset_params_class(asset_type: Literal["text"]) -> type[TextAssetParams]: ...


@overload
def get_asset_params_class(asset_type: Literal["subtitle"]) -> type[TextAssetParams]: ...


@overload
def get_asset_params_class(asset_type: AssetType) -> type[AssetParams]: ...


def get_asset_params_class(asset_type: AssetType) -> type[AssetParams]:
    """
    Get the asset parameters class for the given asset type.

    :param asset_type: The asset type.
    :return: The asset parameters class.
    """
    if asset_type == "subtitle":
        asset_type = "text"

    asset_mod_name = f"mosaico.assets.{asset_type}"

    if not importlib.util.find_spec(asset_mod_name):
        raise InvalidAssetTypeError(asset_type)

    asset_mod = importlib.import_module(asset_mod_name)
    asset_params_class = getattr(asset_mod, f"{asset_type.capitalize()}AssetParams")

    return asset_params_class
