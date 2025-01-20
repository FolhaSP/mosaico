from __future__ import annotations

import io
from typing import Any, Literal

from pydantic import BaseModel
from pydantic.fields import Field
from pydantic.types import NonNegativeInt, PositiveFloat
from pydub import AudioSegment
from tinytag import TinyTag
from typing_extensions import Self

from mosaico.assets.base import BaseAsset
from mosaico.assets.utils import check_user_provided_required_keys
from mosaico.media import _load_file
from mosaico.types import FilePath


class AudioAssetParams(BaseModel):
    """Represents the parameters for an Audio assets."""

    volume: float = Field(default=1.0)
    """The volume of the audio assets."""

    crop: tuple[int, int] | None = None
    """Crop range for the audio assets"""


class AudioAsset(BaseAsset[AudioAssetParams]):
    """Represents an Audio asset with various properties."""

    type: Literal["audio"] = "audio"
    """The type of the asset. Defaults to "audio"."""

    params: AudioAssetParams = Field(default_factory=AudioAssetParams)
    """The parameters for the asset."""

    duration: PositiveFloat
    """The duration of the audio asset."""

    sample_rate: PositiveFloat
    """The sample rate of the audio asset."""

    sample_width: NonNegativeInt
    """The sample width of the audio asset."""

    channels: int
    """The number of channels in the audio asset."""

    @classmethod
    def from_data(
        cls,
        data: str | bytes,
        *,
        path: FilePath | None = None,
        metadata: dict | None = None,
        mime_type: str | None = None,
        **kwargs: Any,
    ) -> Self:
        """
        Creates an audio asset from data.

        :param data: The data of the assets.
        :param path: The path to the file.
        :param metadata: The metadata of the assets.
        :param mime_type: The MIME type of the assets.
        :param kwargs: Additional keyword arguments to the constructor.
        :return: The assets.
        """
        if not check_user_provided_required_keys(kwargs, ["duration", "sample_rate", "sample_width", "channels"]):
            audio_info = _extract_audio_info(data)
            kwargs.update(audio_info)

        return super().from_data(data, path=path, metadata=metadata, mime_type=mime_type, **kwargs)

    @classmethod
    def from_path(
        cls,
        path: FilePath,
        *,
        encoding: str = "utf-8",
        mime_type: str | None = None,
        guess_mime_type: bool = True,
        metadata: dict | None = None,
        **kwargs: Any,
    ) -> Self:
        """
        Creates an audio asset from a file path.

        :param path: The path to the file.
        :param encoding: The encoding of the file.
        :param metadata: The metadata of the assets.
        :param mime_type: The MIME type of the assets.
        :param guess_mime_type: Whether to guess the MIME type.
        :param kwargs: Additional keyword arguments to the constructor.
        :return: The assets.
        """
        storage_options = kwargs.pop("storage_options", None)

        if not check_user_provided_required_keys(kwargs, ["duration", "sample_rate", "sample_width", "channels"]):
            raw_audio = _load_file(path, storage_options=storage_options)
            audio_info = _extract_audio_info(raw_audio)
            kwargs.update(audio_info)

        return super().from_path(
            path, encoding=encoding, mime_type=mime_type, guess_mime_type=guess_mime_type, metadata=metadata, **kwargs
        )

    def slice(self, start_time: float, end_time: float, *, storage_options: dict[str, Any] | None = None) -> AudioAsset:
        """
        Slices the audio asset.

        :param start_time: The start time in seconds.
        :param end_time: The end time in seconds.
        :param storage_options: The storage options.
        :return: The sliced audio asset.
        """
        with self.to_bytes_io(storage_options=storage_options) as audio_file:
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
                duration=audio.duration_seconds,
                sample_rate=self.sample_rate,
                sample_width=self.sample_width,
                channels=self.channels,
            )


def _extract_audio_info(audio: FilePath | bytes) -> dict:
    """
    Extracts the audio information from the audio data.
    """
    if isinstance(audio, bytes):
        tag = TinyTag.get(file_obj=io.BytesIO(audio))
    else:
        tag = TinyTag.get(audio)
    return {
        "duration": tag.duration,
        "sample_rate": tag.samplerate,
        "sample_width": tag.bitdepth if tag.bitdepth is not None else 0,
        "channels": tag.channels,
    }
