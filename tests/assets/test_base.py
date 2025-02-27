import pytest
from pydantic import BaseModel, ValidationError
from pydantic.fields import Field

from mosaico.assets.base import BaseAsset
from mosaico.media import Media


class TestParams(BaseModel):
    foo: str = "hello"
    bar: int = 42

    __test__ = False


class TestAsset(BaseAsset[TestParams, None]):
    type: str = "test"
    params: TestParams = Field(default_factory=TestParams)

    __test__ = False


def test_asset_creation_with_defaults() -> None:
    asset = TestAsset.from_data("test")
    assert asset.data == "test"
    assert asset.type == "test"
    assert asset.params == TestParams()
    assert isinstance(asset.id, str)


def test_asset_creation_with_custom_params() -> None:
    params = TestParams(foo="world", bar=24)
    asset = TestAsset.from_data("test", params=params)
    assert asset.params == params


def test_asset_creation_with_custom_id() -> None:
    asset = TestAsset.from_data("test", id="test_id")
    assert asset.id == "test_id"


def test_asset_from_media():
    media = Media.from_data("test", id="test_id", metadata={"key": "value"})
    asset = TestAsset.from_media(media)
    assert asset.id == "test_id"
    assert asset.data == "test"
    assert asset.metadata == {"key": "value"}
    assert isinstance(asset.params, TestParams)


def test_asset_creation_with_invalid_params() -> None:
    with pytest.raises(ValidationError):
        TestAsset.from_data("test", params=["invalid"])


@pytest.mark.parametrize("params", [{"foo": "world"}, {"bar": 24}, TestParams(foo="world", bar=24)])
def test_asset_with_params(params):
    asset = TestAsset.from_data("test").with_params(params)
    assert asset.params == TestParams.model_validate(params)


def test_asset_with_params_chaining():
    asset = TestAsset.from_data("test")
    updated_asset = asset.with_params({"foo": "world"}).with_params({"bar": 24})
    assert updated_asset.params.foo == "world"
    assert updated_asset.params.bar == 24


def test_asset_with_params_validation():
    asset = TestAsset.from_data("test")
    with pytest.raises(ValidationError):
        asset.with_params({"foo": "world", "bar": "not_an_int"})


def test_asset_with_empty_params():
    asset = TestAsset.from_data("test")
    updated_asset = asset.with_params({})
    assert updated_asset.params == asset.params


def test_asset_with_invalid_params_type():
    asset = TestAsset.from_data("test")
    with pytest.raises(ValueError):
        asset.with_params("invalid")
