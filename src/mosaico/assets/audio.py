from __future__ import annotations

import io
from typing import Any, Literal, cast

from pydantic import BaseModel
from pydantic.fields import Field
from pydantic.types import NonNegativeInt, PositiveFloat
from pydub import AudioSegment
from pydub.silence import detect_leading_silence
from tinytag import TinyTag

from mosaico.assets.base import BaseAsset


class AudioInfo(BaseModel):
    """
    Represents the audio specific metadata.
    """

    duration: PositiveFloat
    """The duration of the audio asset."""

    sample_rate: PositiveFloat
    """The sample rate of the audio asset."""

    sample_width: NonNegativeInt
    """The sample width of the audio asset."""

    channels: NonNegativeInt
    """The number of channels in the audio asset."""


class AudioAssetParams(BaseModel):
    """
    Represents the parameters for an Audio assets.
    """

    volume: float = Field(default=1.0)
    """The volume of the audio assets."""

    crop: tuple[int, int] | None = None
    """Crop range for the audio assets"""


class AudioAsset(BaseAsset[AudioAssetParams, AudioInfo]):
    """Represents an Audio asset with various properties."""

    type: Literal["audio"] = "audio"  # type: ignore
    """The type of the asset. Defaults to "audio"."""

    params: AudioAssetParams = Field(default_factory=AudioAssetParams)
    """The parameters for the asset."""

    @property
    def duration(self) -> float:
        """
        The duration of the audio asset.

        Wrapper of `AudioAsset.info.duration` for convenience and type-hint compatibility.
        """
        return self._safe_get_info_key("duration")

    @property
    def sample_rate(self) -> float:
        """
        The sample rate of the audio asset.

        Wrapper of `AudioAsset.info.sample_rate` for convenience and type-hint compatibility.
        """
        return self._safe_get_info_key("sample_rate")

    @property
    def sample_width(self) -> int:
        """
        The sample width of the audio asset.

        Wrapper of `AudioAsset.info.sample_width` for convenience and type-hint compatibility.
        """
        return self._safe_get_info_key("sample_width")

    @property
    def channels(self) -> int:
        """
        The number of channels in the audio asset.

        Wrapper of `AudioAsset.info.channels` for convenience and type-hint compatibility.
        """
        return self._safe_get_info_key("channels")

    def to_audio_segment(self, **kwargs) -> AudioSegment:
        """
        Casts the audio asset to a pydub.AudioSegment object.
        """
        with self.to_bytes_io(**kwargs) as audio_buf:
            return AudioSegment.from_file(
                file=audio_buf,
                sample_width=self.sample_width,
                frame_rate=self.sample_rate,
                channels=self.channels,
            )

    def slice(self, start_time: float, end_time: float, **kwargs: Any) -> AudioAsset:
        """
        Slices the audio asset.

        :param start_time: The start time in seconds.
        :param end_time: The end time in seconds.
        :param kwargs: Additional parameters passed to the audio loader.
        :return: The sliced audio asset.
        """
        audio = self.to_audio_segment(**kwargs)

        sliced_buf = io.BytesIO()
        sliced_audio = cast(AudioSegment, audio[round(start_time * 1000) : round(end_time * 1000)])
        sliced_audio.export(sliced_buf, format="mp3")
        sliced_buf.seek(0)

        return AudioAsset.from_data(
            sliced_buf.read(),
            info=AudioInfo(
                duration=len(sliced_audio) / 1000,
                sample_rate=self.sample_rate,
                sample_width=self.sample_width,
                channels=self.channels,
            ),
        )

    def strip_silence(self, silence_threshold: float = -50, chunk_size: int = 10, **kwargs: Any) -> AudioAsset:
        """
        Removes leading and trailing silence from the audio asset.

        :param silence_threshold: Silence threshold in dBFS (default: -50.0).
        :param chunk_size: Size of the audio iterator chunk, in ms (default: 10).
        :param kwargs: Additional parameters passed to the audio loader.
        :return: A new AudioAsset with leading and trailing silence removed.
        """
        audio = self.to_audio_segment(**kwargs)
        start_trim = detect_leading_silence(audio, silence_threshold, chunk_size)
        end_trim = detect_leading_silence(audio.reverse(), silence_threshold, chunk_size)
        return self.slice(start_trim / 1000, (len(audio) - end_trim) / 1000)

    def _load_info(self) -> None:
        attrs = ["duration", "sample_rate", "sample_width", "channels"]
        if self.info is not None and all(getattr(self.info, attr) is not None for attr in attrs):
            return
        audio = self.data
        if audio is not None:
            if isinstance(audio, str):
                audio = audio.encode("utf-8")
        else:
            audio = self.to_bytes()
            self.data = audio
        tag = TinyTag.get(file_obj=io.BytesIO(audio))
        self.info = AudioInfo(
            duration=tag.duration or 0,
            sample_rate=tag.samplerate or 0,
            sample_width=tag.bitdepth if tag.bitdepth is not None else 0,
            channels=tag.channels or 0,
        )
