from __future__ import annotations

import importlib
import importlib.util
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Literal, cast, overload

from moviepy.Clip import Clip

from mosaico.clip_makers.base import BaseClipMaker
from mosaico.exceptions import InvalidAssetTypeError


if TYPE_CHECKING:
    from mosaico.assets.audio import AudioAsset
    from mosaico.assets.image import ImageAsset
    from mosaico.assets.subtitle import SubtitleAsset
    from mosaico.assets.text import TextAsset
    from mosaico.assets.types import Asset, AssetType
    from mosaico.clip_makers.protocol import ClipMaker
    from mosaico.effects.protocol import Effect
    from mosaico.types import FrameSize


@overload
def get_clip_maker_class(asset_type: Literal["text"]) -> type[ClipMaker[TextAsset]]: ...


@overload
def get_clip_maker_class(asset_type: Literal["subtitle"]) -> type[ClipMaker[SubtitleAsset]]: ...


@overload
def get_clip_maker_class(asset_type: Literal["audio"]) -> type[ClipMaker[AudioAsset]]: ...


@overload
def get_clip_maker_class(asset_type: Literal["image"]) -> type[ClipMaker[ImageAsset]]: ...


@overload
def get_clip_maker_class(asset_type: AssetType) -> type[ClipMaker]: ...


def get_clip_maker_class(asset_type: AssetType) -> type[ClipMaker]:
    """
    Get a clip maker class.

    :param asset_type: The assets type.
    :return: The clip maker class.
    :raises ValueError: If no clip maker is found for the given assets type and name.
    """
    cm_mod_name = f"mosaico.clip_makers.{asset_type}"

    if not importlib.util.find_spec(cm_mod_name):
        raise InvalidAssetTypeError(asset_type)

    cm_mod = importlib.import_module(f"mosaico.clip_makers.{asset_type}")
    cm_class = getattr(cm_mod, asset_type.capitalize() + "ClipMaker")

    return cm_class


def make_clip(
    asset: Asset,
    duration: float | None = None,
    video_resolution: FrameSize | None = None,
    effects: Sequence[Effect] | None = None,
    storage_options: dict[str, Any] | None = None,
    **kwargs: Any,
) -> Clip:
    """
    Make a clip from the given asset.

    :param asset: The asset.
    :param duration: The duration of the clip.
    :param video_resolution: The resolution of the video.
    :return: The clip.
    """
    clip_maker_cls = get_clip_maker_class(asset.type)
    clip_maker_cls = cast(type[BaseClipMaker], clip_maker_cls)
    clip_maker = clip_maker_cls(
        duration=duration,
        video_resolution=video_resolution,
        effects=list(effects) if effects is not None else [],
        storage_options=storage_options if storage_options is not None else {},
        **kwargs,
    )
    return clip_maker.make_clip(asset)
