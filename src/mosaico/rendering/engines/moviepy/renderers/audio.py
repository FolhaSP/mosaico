from __future__ import annotations

from tempfile import NamedTemporaryFile
from typing import Any

from moviepy.audio import fx as afx
from moviepy.audio.io.AudioFileClip import AudioFileClip as MPAudioFileClip
from pydub import AudioSegment

from mosaico.assets.audio import AudioAsset
from mosaico.assets.clip import AssetClip
from mosaico.rendering.engines.protocol import AssetClipRenderer
from mosaico.rendering.types import RenderingOptions


class MoviepyAudioClipRenderer(AssetClipRenderer[AudioAsset]):
    """
    A Moviepy clip renderer for audio assets.

    The audio clip renderer performs these transformations:

    1. Loads raw audio data into PyDub format
    2. Crops if needed to match clip duration
    3. Exports audio to temporary MP3 file

    __Examples__:

    ```python
    # Setup asset and asset clip
    asset = AudioAsset("path/to/audio.mp3")
    clip = AssetClip.from_asset(asset, duration=5.0)

    # Project configuration
    config = VideoProjectConfig()

    # Create a basic audio clip
    renderer = AudioClipRenderer()
    rendered_clip = renderer.render(clip, asset, config)
    ```
    """

    def render(self, clip: AssetClip, asset: AudioAsset, options: RenderingOptions) -> Any:
        """
        Make a clip from the given audio asset.

        :asset: The audio asset to make the clip from.
        :return: The audio clip.
        """
        clip_duration = clip.duration or asset.duration

        with (
            asset.to_bytes_io() as audio_buf,
            NamedTemporaryFile(mode="wb", suffix=".mp3") as temp_file,
        ):
            audio = AudioSegment.from_file(
                file=audio_buf,
                sample_width=asset.sample_width,
                frame_rate=asset.sample_rate,
                channels=asset.channels,
            )

            if asset.duration > clip_duration:
                audio = audio[: round(clip_duration * 1000)]

            if asset.params.crop is not None:
                audio = audio[asset.params.crop[0] * 1000 : asset.params.crop[1] * 1000]

            audio.export(temp_file.name, format="mp3")

            return (
                MPAudioFileClip(temp_file.name)
                .with_fps(options.fps)
                .with_effects([afx.MultiplyVolume(asset.params.volume)])
            )
