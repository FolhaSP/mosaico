from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, PositiveInt
from pydantic.fields import PrivateAttr
from pydantic.functional_validators import model_validator
from pydantic_extra_types.language_code import LanguageAlpha2
from typing_extensions import Self

from mosaico.assets.audio import AudioAsset
from mosaico.audio_transcribers.transcription import Transcription, TranscriptionWord
from mosaico.types import ModelTemperature


class OpenAIWhisperTranscriber(BaseModel):
    """Transcriber using OpenAI's Whisper API."""

    api_key: str | None = None
    """API key for OpenAI's Whisper API."""

    base_url: str | None = None
    """Base URL for OpenAI's Whisper API."""

    timeout: PositiveInt = 120
    """Timeout for transcription in seconds."""

    model: Literal["whisper-1"] = "whisper-1"
    """Model to use for transcription."""

    temperature: ModelTemperature = 0
    """The sampling temperature for the model."""

    language: LanguageAlpha2 | None = None
    """Language of the transcription."""

    _client: Any = PrivateAttr(default=None)
    """OpenAI client."""

    @model_validator(mode="after")
    def _set_client(self) -> Self:
        """
        Set the OpenAI API client.
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI package is required for OpenAIWhisperTranscriber.")
        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)
        return self

    def transcribe(self, audio_asset: AudioAsset) -> Transcription:
        """
        Transcribe audio using OpenAI's Whisper API.

        :param audio_asset: The audio asset to transcribe.
        :return: The transcription words.
        """
        with audio_asset.to_bytes_io() as audio_file:
            audio_file.name = f"{audio_asset.id}.mp3"  # type: ignore
            response = self._client.audio.transcriptions.create(
                file=audio_file,
                model=self.model,
                temperature=self.temperature,
                language=str(self.language) if self.language is not None else "",
                response_format="verbose_json",
                timestamp_granularities=["word"],
            )

        if not response.words:
            raise ValueError("No words found in transcription response.")

        words = [TranscriptionWord(start_time=word.start, end_time=word.end, text=word.word) for word in response.words]

        return Transcription(words=words)
