from __future__ import annotations

from typing import cast

from moviepy.Clip import Clip
from moviepy.video.VideoClip import ImageClip

from mosaico.assets.text import BaseTextAsset
from mosaico.clip_makers.text import TextClipMaker


class SubtitleClipMaker(TextClipMaker):
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

    def _make_clip(self, asset: BaseTextAsset) -> Clip:
        """
        Create a clip from a subtitle asset.

        :param asset: The subtitle asset.
        :return: The subtitle clip.
        """
        clip = super()._make_clip(asset)
        clip = cast(ImageClip, clip)
        video_resolution = cast(tuple[int, int], self.video_resolution)
        position = asset.params.position

        match position.y:
            case "top":
                clip = clip.set_position(("center", video_resolution[1] * 0.2))
            case "bottom":
                clip = clip.set_position(("center", video_resolution[1] * 0.8 - clip.h // 2))
            case _:
                clip = clip.set_position(("center", "center"))

        return clip
