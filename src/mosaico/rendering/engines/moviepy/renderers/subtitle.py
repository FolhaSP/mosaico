from __future__ import annotations

from typing import Any, cast

from moviepy.video.VideoClip import ImageClip

from mosaico.assets.clip import AssetClip
from mosaico.assets.text import BaseTextAsset, TextAssetParams
from mosaico.rendering.engines.moviepy.renderers.text import MoviepyTextClipRenderer
from mosaico.rendering.types import RenderingOptions


class MoviepySubtitleClipRenderer(MoviepyTextClipRenderer):
    """
    A clip maker for subtitle assets.

    The subtitle clip maker performs these transformations:

    1. Execute the text clip maker process
    2. Position the subtitle at the top, bottom, or center of the video
    3. Return the subtitle clip

    !!! note
        For further details, refer to the [TextClipMaker](./text.md) documentation.

    __Examples__:

    ```python
    # Create a basic subtitle clip
    maker = SubtitleClipMaker(duration=5.0, video_resolution=(1920, 1080))
    clip = maker.make_clip(subtitle_asset)
    ```
    """

    def render(self, clip: AssetClip, asset: BaseTextAsset, options: RenderingOptions) -> Any:
        """
        Create a clip from a subtitle asset.

        :param asset: The subtitle asset.
        :return: The subtitle clip.
        """
        _, max_height = options.resolution
        subtitle_clip = cast(ImageClip, super().render(clip, asset, options))
        params = cast(TextAssetParams, clip.asset_reference.params) or asset.params

        match params.position.y:
            case "top":
                subtitle_clip = subtitle_clip.with_position(("center", max_height * 0.2))
            case "bottom":
                subtitle_clip = subtitle_clip.with_position(("center", max_height * 0.8 - subtitle_clip.h // 2))
            case _:
                subtitle_clip = subtitle_clip.with_position(("center", "center"))

        return subtitle_clip
