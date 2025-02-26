from __future__ import annotations

import io
from typing import Any, Literal

from pydantic import BaseModel
from pydantic.fields import Field
from pydantic.types import NonNegativeInt, PositiveFloat
from pydub import AudioSegment
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

    def slice(self, start_time: float, end_time: float, **kwargs: Any) -> AudioAsset:
        """
        Slices the audio asset.

        :param start_time: The start time in seconds.
        :param end_time: The end time in seconds.
        :return: The sliced audio asset.
        """
        with self.to_bytes_io(**kwargs) as audio_file:
            audio = AudioSegment.from_file(
                file=audio_file,
                sample_width=self.sample_width,
                frame_rate=self.sample_rate,
                channels=self.channels,
            )

            sliced_buf = io.BytesIO()
            sliced_audio = audio[round(start_time * 1000) : round(end_time * 1000)]
            sliced_audio.export(sliced_buf, format="mp3")
            sliced_buf.seek(0)

            return AudioAsset.from_data(
                sliced_buf.read(),
                info=AudioInfo(
                    duration=audio.duration_seconds,
                    sample_rate=self.sample_rate,
                    sample_width=self.sample_width,
                    channels=self.channels,
                ),
            )

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
