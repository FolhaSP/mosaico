import io
from unittest.mock import patch

import cv2 as cv
import numpy as np
import pytest
from moviepy.video.VideoClip import ImageClip
from PIL import Image

from mosaico.assets.image import ImageAsset
from mosaico.clip_makers.image import ImageClipMaker, _resize_and_crop
from mosaico.positioning.absolute import AbsolutePosition
from mosaico.positioning.relative import RelativePosition


@pytest.fixture
def transparent_png_data():
    """Create a PNG with transparency (RGBA)."""
    img = Image.new("RGBA", (200, 200), (0, 0, 0, 0))  # Transparent background
    # Draw a red square in the center
    for x in range(50, 150):
        for y in range(50, 150):
            img.putpixel((x, y), (255, 0, 0, 255))  # Red with full alpha

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    return img_bytes.getvalue()


@pytest.fixture
def opaque_png_data():
    """Create an opaque PNG (RGB saved as PNG)."""
    img = Image.new("RGB", (200, 200), (0, 255, 0))  # Green background
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    return img_bytes.getvalue()


@pytest.fixture
def jpeg_data():
    """Create JPEG data for comparison."""
    img = Image.new("RGB", (200, 200), (0, 0, 255))  # Blue background
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    return img_bytes.getvalue()


@pytest.fixture
def clip_maker():
    """Create a standard image clip maker."""
    return ImageClipMaker(duration=5.0, video_resolution=(1920, 1080))


def test_make_clip_requires_video_resolution():
    """Test that video_resolution is required."""
    clip_maker = ImageClipMaker(duration=5.0, video_resolution=None)
    asset = ImageAsset.from_data(b"fake_data")

    with pytest.raises(ValueError, match="video_resolution is required"):
        clip_maker.make_clip(asset)


def test_make_clip_requires_duration(transparent_png_data):
    """Test that duration is required."""
    clip_maker = ImageClipMaker(duration=None, video_resolution=(1920, 1080))
    asset = ImageAsset.from_data(transparent_png_data)

    with pytest.raises(ValueError, match="duration is required"):
        clip_maker.make_clip(asset)


def test_make_clip_transparent_png(clip_maker, transparent_png_data):
    """Test creating clip from transparent PNG."""
    asset = ImageAsset.from_data(transparent_png_data)
    asset.params.position = AbsolutePosition(x=0, y=0)
    asset.params.as_background = False

    clip = clip_maker.make_clip(asset)

    assert isinstance(clip, ImageClip)
    assert clip.duration == 5.0
    assert clip.size == (200, 200)


def test_make_clip_opaque_png(clip_maker, opaque_png_data):
    """Test creating clip from opaque PNG."""
    asset = ImageAsset.from_data(opaque_png_data)
    asset.params.position = AbsolutePosition(x=100, y=100)
    asset.params.as_background = False

    clip = clip_maker.make_clip(asset)

    assert isinstance(clip, ImageClip)
    assert clip.duration == 5.0
    assert clip.size == (200, 200)


def test_make_clip_with_relative_position(clip_maker, transparent_png_data):
    """Test creating clip with relative positioning."""
    asset = ImageAsset.from_data(transparent_png_data)
    asset.params.position = RelativePosition(x=0.5, y=0.5)
    asset.params.as_background = False

    clip = clip_maker.make_clip(asset)

    assert isinstance(clip, ImageClip)
    assert clip.duration == 5.0


def test_make_clip_as_background_resizes(clip_maker, transparent_png_data):
    """Test that as_background=True triggers resize."""
    asset = ImageAsset.from_data(transparent_png_data)
    asset.params.position = AbsolutePosition(x=0, y=0)
    asset.params.as_background = True

    clip = clip_maker.make_clip(asset)

    assert isinstance(clip, ImageClip)
    assert clip.duration == 5.0
    # After resize, should match video resolution
    assert clip.size == (1920, 1080)


def test_make_clip_no_resize_when_same_resolution(transparent_png_data):
    """Test that no resize occurs when asset size matches video resolution."""
    # Create asset with same size as video resolution
    asset = ImageAsset.from_data(transparent_png_data)
    asset.params.position = AbsolutePosition(x=0, y=0)
    asset.params.as_background = True

    # Mock the size property to return video resolution dimensions
    with patch.object(type(asset), "size", new_callable=lambda: property(lambda _: (1920, 1080))):
        clip_maker = ImageClipMaker(duration=3.0, video_resolution=(1920, 1080))

        with patch("mosaico.clip_makers.image._resize_and_crop") as mock_resize:
            clip = clip_maker.make_clip(asset)

            # _resize_and_crop should not be called
            mock_resize.assert_not_called()
            assert isinstance(clip, ImageClip)


def test_resize_and_crop_wider_image():
    """Test resizing wider image (crop sides)."""
    # Create a wide image (400x200)
    image = np.ones((200, 400, 3), dtype=np.uint8) * 255
    target_size = (200, 200)  # Square target

    result = _resize_and_crop(image, target_size)

    assert result.shape[:2] == (200, 200)
    assert result.shape[2] == 3


def test_resize_and_crop_taller_image():
    """Test resizing taller image (crop top/bottom)."""
    # Create a tall image (200x400)
    image = np.ones((400, 200, 3), dtype=np.uint8) * 255
    target_size = (200, 200)  # Square target

    result = _resize_and_crop(image, target_size)

    assert result.shape[:2] == (200, 200)
    assert result.shape[2] == 3


def test_resize_and_crop_square_to_rectangle():
    """Test resizing square image to rectangle."""
    # Create a square image (200x200)
    image = np.ones((200, 200, 3), dtype=np.uint8) * 255
    target_size = (400, 200)  # Wide rectangle

    result = _resize_and_crop(image, target_size)

    assert result.shape[:2] == (200, 400)
    assert result.shape[2] == 3


def test_resize_and_crop_preserves_channels():
    """Test that channel count is preserved."""
    # Test with 4-channel image (RGBA)
    image = np.ones((200, 200, 4), dtype=np.uint8) * 255
    target_size = (300, 300)

    result = _resize_and_crop(image, target_size)

    assert result.shape[:2] == (300, 300)
    assert result.shape[2] == 4  # Alpha channel preserved


def test_resize_and_crop_grayscale():
    """Test with grayscale image."""
    # Create grayscale image
    image = np.ones((200, 200), dtype=np.uint8) * 128
    target_size = (100, 100)

    result = _resize_and_crop(image, target_size)

    assert result.shape == (100, 100)

