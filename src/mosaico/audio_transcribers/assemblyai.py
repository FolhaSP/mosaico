from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from pydantic import BaseModel
from pydantic.fields import PrivateAttr
from pydantic.functional_validators import model_validator
from pydantic_extra_types.language_code import LanguageAlpha2
from typing_extensions import Self

from mosaico.assets.audio import AudioAsset
from mosaico.audio_transcribers.transcription import Transcription, TranscriptionWord


class AssemblyAIAudioTranscriber(BaseModel):
    """Transcriber using AssemblyAI's API."""

    api_key: str | None = None
    """API key for AssemblyAI."""

    model: Literal["best", "nano"] = "best"
    """Model to use for transcription."""

    language: LanguageAlpha2 | None = None
    """Language of the transcription."""

    custom_spelling: dict[str, str | Sequence[str]] | None = None
    """Custom spelling dictionary for the transcription."""

    _client: Any = PrivateAttr(default=None)
    """AssemblyAI client."""

    @model_validator(mode="after")
    def _set_client(self) -> Self:
        """
        Set the AssemblyAI API client.
        """
        try:
            import assemblyai as aai
        except ImportError:
            raise ImportError("AssemblyAI package is required for AssemblyAIAudioTranscriber.")
        settings = aai.Settings()
        settings.api_key = self.api_key
        self._client = aai.Client(settings=settings)
        return self

    def transcribe(self, audio_asset: AudioAsset) -> Transcription:
        """
        Transcribe audio using AssemblyAI's API.

        :param audio_asset:
        :return: The transcription.
        """
        try:
            import assemblyai as aai
        except ImportError:
            raise ImportError("AssemblyAI package is required for AssemblyAIAudioTranscriber.")

        config = aai.TranscriptionConfig(
            speech_model=aai.SpeechModel(self.model),
            language_code=str(self.language) if self.language else None,
            language_detection=self.language is None,
            custom_spelling=self.custom_spelling,
            punctuate=True,
            format_text=True,
        )

        transcriber = aai.Transcriber(client=self._client, config=config)

        with audio_asset.to_bytes_io() as audio_file:
            response = transcriber.transcribe(audio_file)

        transcription = response.wait_for_completion()

        if transcription.words is None:
            raise ValueError("No word timestamps found in transcription.")

        return Transcription(
            words=[
                TranscriptionWord(start_time=word.start / 1000, end_time=word.end / 1000, text=word.text)
                for word in transcription.words
            ]
        )
