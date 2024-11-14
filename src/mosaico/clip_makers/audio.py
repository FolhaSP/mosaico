from __future__ import annotations

from tempfile import NamedTemporaryFile

from moviepy.audio.fx.volumex import volumex
from moviepy.Clip import Clip
from moviepy.editor import AudioFileClip
from pydub import AudioSegment

from mosaico.assets.audio import AudioAsset
from mosaico.clip_makers.base import BaseClipMaker


class AudioClipMaker(BaseClipMaker[AudioAsset]):
    """
    A clip maker for audio assets.

    The audio clip maker performs these transformations:

    1. Loads raw audio data into PyDub format
    2. Crops if needed to match clip duration
    3. Exports audio to temporary MP3 file

    __Examples__:

    ```python
    # Create a basic audio clip
    maker = AudioClipMaker(duration=5.0)
    clip = maker.make_clip(audio_asset)

    # Create clip with custom duration
    clip = maker.make_clip(audio_asset, duration=10.0)
    ```
    """

    def _make_clip(self, asset: AudioAsset) -> Clip:
        """
        Make a clip from the given audio asset.

        :asset: The audio asset to make the clip from.
        :return: The audio clip.
        """
        clip_duration = self.duration if self.duration is not None else asset.duration

        with asset.to_bytes_io() as audio_buf, NamedTemporaryFile(mode="wb", suffix=".mp3") as temp_file:
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

            return AudioFileClip(temp_file.name, fps=asset.sample_rate).fx(volumex, asset.params.volume)
