import io
from pathlib import Path

import pytest
from PIL import Image

from mosaico.assets.image import ImageAsset


@pytest.fixture
def sample_image_data():
    # Create a simple test image in memory
    img = Image.new("RGB", (100, 50), color="red")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()


@pytest.fixture
def sample_image_path(tmp_path, sample_image_data):
    # Create a temporary image file
    image_path = tmp_path / "test_image.png"
    with open(image_path, "wb") as f:
        f.write(sample_image_data)
    return image_path


def test_image_asset_from_data(sample_image_data):
    # Test creating ImageAsset from raw data
    image_asset = ImageAsset.from_data(sample_image_data)

    assert image_asset.type == "image"
    assert image_asset.width == 100
    assert image_asset.height == 50
    assert image_asset.data == sample_image_data


def test_image_asset_from_data_with_explicit_dimensions(sample_image_data):
    # Test creating ImageAsset with explicitly provided dimensions
    image_asset = ImageAsset.from_data(sample_image_data, width=200, height=100)

    assert image_asset.width == 200
    assert image_asset.height == 100
    assert image_asset.data == sample_image_data


def test_image_asset_from_path(sample_image_path):
    # Test creating ImageAsset from file path
    image_asset = ImageAsset.from_path(sample_image_path)

    assert image_asset.type == "image"
    assert image_asset.width == 100
    assert image_asset.height == 50

    with open(sample_image_path, "rb") as f:
        expected_data = f.read()

    assert image_asset.to_bytes() == expected_data


def test_image_asset_from_path_with_explicit_dimensions(sample_image_path):
    # Test creating ImageAsset from path with explicitly provided dimensions
    image_asset = ImageAsset.from_path(sample_image_path, width=300, height=150)

    assert image_asset.width == 300
    assert image_asset.height == 150

    with open(sample_image_path, "rb") as f:
        expected_data = f.read()

    assert image_asset.to_bytes() == expected_data


def test_image_asset_from_path_with_pathlib(sample_image_path):
    # Test creating ImageAsset using Path object
    path_obj = Path(sample_image_path)
    image_asset = ImageAsset.from_path(path_obj)

    assert image_asset.type == "image"
    assert image_asset.width == 100
    assert image_asset.height == 50


def test_image_asset_from_invalid_data():
    # Test handling invalid image data
    with pytest.raises(Exception):
        ImageAsset.from_data(b"invalid image data")


def test_image_asset_from_invalid_path():
    # Test handling non-existent file path
    with pytest.raises(FileNotFoundError):
        ImageAsset.from_path("nonexistent_image.png")


def test_image_asset_params_default_values(sample_image_data):
    # Test default parameter values
    image_asset = ImageAsset.from_data(sample_image_data)

    assert image_asset.params.z_index == -1
    assert image_asset.params.crop is None
    assert image_asset.params.as_background is True


def test_image_asset_with_metadata(sample_image_data):
    # Test creating ImageAsset with metadata
    metadata = {"author": "Test User", "created": "2023-01-01"}
    image_asset = ImageAsset.from_data(sample_image_data, metadata=metadata)

    assert image_asset.metadata == metadata


# def test_image_asset_from_remote_path(mocker, sample_image_data):
#     # Mock the _load_file function to simulate remote file loading
#     mock_load_file = mocker.patch("mosaico.media._load_file")
#     mock_load_file.return_value = sample_image_data

#     remote_path = "https://f.i.uol.com.br/fotografia/2022/02/09/16444170036203cfeb9fbd1_1644417003_3x2_md.jpg"
#     image_asset = ImageAsset.from_path(remote_path)

#     assert image_asset.type == "image"
#     assert image_asset.width == 100
#     assert image_asset.height == 50
#     assert image_asset.to_bytes() == sample_image_data


# def test_image_asset_from_remote_path_with_explicit_dimensions(mocker, sample_image_data):
#     # Mock the _load_file function to simulate remote file loading
#     mock_load_file = mocker.patch("mosaico.media._load_file")
#     mock_load_file.return_value = sample_image_data

#     remote_path = "https://f.i.uol.com.br/fotografia/2022/02/09/16444170036203cfeb9fbd1_1644417003_3x2_md.jpg"
#     image_asset = ImageAsset.from_path(remote_path, width=300, height=150)

#     assert image_asset.width == 300
#     assert image_asset.height == 150
#     assert image_asset.to_bytes() == sample_image_data


# def test_image_asset_from_remote_path_with_metadata(mocker, sample_image_data):
#     # Mock the _load_file function to simulate remote file loading
#     mock_load_file = mocker.patch("mosaico.media._load_file")
#     mock_load_file.return_value = sample_image_data

#     remote_path = "https://f.i.uol.com.br/fotografia/2022/02/09/16444170036203cfeb9fbd1_1644417003_3x2_md.jpg"
#     metadata = {"author": "Test User", "created": "2023-01-01"}
#     image_asset = ImageAsset.from_path(remote_path, metadata=metadata)

#     assert image_asset.metadata == metadata
#     assert image_asset.to_bytes() == sample_image_data
