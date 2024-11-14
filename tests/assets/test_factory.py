import pytest

from mosaico.assets.factory import create_asset, get_asset_params_class
from mosaico.assets.types import AssetType
from mosaico.exceptions import InvalidAssetTypeError


@pytest.mark.parametrize(
    "asset_type, inputs",
    [
        ("image", {"data": b"Hello", "width": 100, "height": 100}),
        ("audio", {"data": b"Hello", "duration": 10, "sample_rate": 44100, "sample_width": 16, "channels": 1}),
        ("text", {"data": "Hello"}),
        ("subtitle", {"data": "Subtitle"}),
    ],
    ids=["image", "audio", "text", "subtitle"],
)
def test_create_asset(asset_type, inputs):
    asset = create_asset(asset_type, **inputs)
    assert asset.type == asset_type
    assert all(getattr(asset, k) == v for k, v in inputs.items())


def test_get_invalid_asset_type():
    with pytest.raises(InvalidAssetTypeError):
        create_asset("invalid", data="Hello")


@pytest.mark.parametrize(
    "asset_type,expected_type_name",
    [
        ("image", "ImageAssetParams"),
        ("audio", "AudioAssetParams"),
        ("text", "TextAssetParams"),
        ("subtitle", "TextAssetParams"),
    ],
    ids=["image", "audio", "text", "subtitle"],
)
def test_get_asset_params_class(asset_type: AssetType, expected_type_name: str) -> None:
    params_class = get_asset_params_class(asset_type)
    assert params_class.__name__ == expected_type_name
