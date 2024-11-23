from unittest.mock import Mock, patch

import pytest
from moviepy.video.VideoClip import Clip

from mosaico.assets.types import Asset, AssetType
from mosaico.clip_makers.base import BaseClipMaker
from mosaico.clip_makers.factory import get_clip_maker_class, make_clip
from mosaico.effects.protocol import Effect
from mosaico.exceptions import InvalidAssetTypeError


@pytest.mark.parametrize("asset_type", ["audio", "image", "text", "subtitle"])
def test_get_clip_maker(asset_type: AssetType) -> None:
    clip_maker = get_clip_maker_class(asset_type)
    assert clip_maker.__name__.startswith(asset_type.capitalize())


def test_get_clip_maker_invalid_type() -> None:
    with pytest.raises(InvalidAssetTypeError):
        get_clip_maker_class("invalid_type")


@patch("mosaico.clip_makers.factory.get_clip_maker_class")
def test_make_clip(mock_get_clip_maker_class) -> None:
    mock_asset = Mock(spec=Asset, type="image")
    mock_clip = Mock(spec=Clip)
    mock_clip_maker_cls = Mock(spec=BaseClipMaker)
    mock_clip_maker = mock_clip_maker_cls.return_value
    mock_clip_maker.make_clip.return_value = mock_clip

    mock_get_clip_maker_class.return_value = mock_clip_maker_cls

    duration = 10.0
    video_resolution = (1920, 1080)
    effects = [Mock(spec=Effect)]
    storage_options = {}
    kwargs = {"extra_arg": "value"}

    result = make_clip(
        asset=mock_asset,
        duration=duration,
        video_resolution=video_resolution,
        effects=effects,
        storage_options=storage_options,
        **kwargs,
    )

    mock_get_clip_maker_class.assert_called_once_with(mock_asset.type)
    mock_clip_maker_cls.assert_called_once_with(
        duration=duration, video_resolution=video_resolution, effects=effects, storage_options=storage_options, **kwargs
    )
    mock_clip_maker_cls.return_value.make_clip.assert_called_once_with(mock_asset)
    assert result == mock_clip


def test_make_clip_invalid_type():
    asset = Mock(spec=Asset)
    asset.type = "invalid_type"
    duration = 10.0
    video_resolution = (1920, 1080)

    with pytest.raises(InvalidAssetTypeError):
        make_clip(asset, duration, video_resolution)
