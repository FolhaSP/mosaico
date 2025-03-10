from __future__ import annotations

import tempfile
from typing import Any, cast

import cv2 as cv
import numpy as np
from moviepy.video.VideoClip import ImageClip as MoviepyImageClip

from mosaico.assets.clip import AssetClip
from mosaico.assets.image import ImageAsset, ImageAssetParams
from mosaico.positioning.utils import is_relative_position
from mosaico.rendering.engines.protocol import AssetClipRenderer
from mosaico.rendering.types import RenderingOptions


class MoviepyImageClipRenderer(AssetClipRenderer[ImageAsset]):
    """
    A clip maker for image assets.

    The image clip maker performs these transformations:

    1. Loads raw image data into OpenCV format
    2. Resizes/crops if needed to match video resolution
    3. Creates temporary image file
    4. Constructs MoviePy ImageClip with:
        - Image data from temp file
        - Position from asset params
        - Duration from clip maker config

    __Examples__:

    ```python
    # Create a basic image clip
    maker = ImageClipMaker(duration=5.0, video_resolution=(1920, 1080))
    clip = maker.make_clip(image_asset)

    # Create clip with background resize
    image_asset.params.as_background = True
    clip = maker.make_clip(image_asset)  # Will resize to match resolution

    # Create clip with custom position
    image_asset.params.position = AbsolutePosition(x=100, y=50)
    clip = maker.make_clip(image_asset)  # Will position at x=100, y=50
    ```
    """

    def render(self, clip: AssetClip, asset: ImageAsset, options: RenderingOptions) -> Any:
        """
        Render the image asset as a MoviePy clip.

        :param clip: The asset clip to render.
        :param asset: The image asset to render.
        :param options: The rendering options.
        :return: A Moviepy image clip.
        """
        params = cast(ImageAssetParams, clip.asset_reference.params) or asset.params
        position = params.position

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".jpg") as fp:
            nparr = np.frombuffer(asset.to_bytes(), np.uint8)
            image = cv.imdecode(nparr, cv.IMREAD_COLOR)

            # Resize the image if it's not the same resolution as the video
            if asset.size != options.resolution and params.as_background:
                image = _resize_and_crop(image, options.resolution)

            cv.imwrite(fp.name, image)

            return (
                MoviepyImageClip(img=fp.name)
                .with_layer_index(params.z_index)
                .with_position((position.x, position.y), relative=is_relative_position(position))
                .with_start(clip.start_time)
                .with_duration(clip.duration or 3)
                .with_fps(options.fps)
            )


def _resize_and_crop(image: cv.typing.MatLike, target_size: tuple[int, int]) -> cv.typing.MatLike:
    """
    Resize and crop an image to the target size.
    """
    target_w, target_h = target_size
    h, w = image.shape[:2]

    # Calculate aspect ratios
    aspect_ratio_target = target_w / target_h
    aspect_ratio_image = w / h

    if aspect_ratio_image > aspect_ratio_target:
        # Image is wider, crop the sides
        new_w = int(h * aspect_ratio_target)
        new_h = h
        start_x = (w - new_w) // 2
        start_y = 0
    else:
        # Image is taller, crop the top and bottom
        new_w = w
        new_h = int(w / aspect_ratio_target)
        start_x = 0
        start_y = (h - new_h) // 2

    # Crop the image
    cropped = image[start_y : start_y + new_h, start_x : start_x + new_w]

    # Resize to target size
    resized = cv.resize(cropped, target_size, interpolation=cv.INTER_CUBIC)

    return resized
