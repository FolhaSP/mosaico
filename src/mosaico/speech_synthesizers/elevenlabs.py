import io
import os
from collections.abc import Sequence
from typing import Annotated, Any, ClassVar, Literal

import requests
from pydantic import BaseModel
from pydantic.fields import Field
from pydantic_extra_types.language_code import LanguageAlpha2
from pydub import AudioSegment

from mosaico.assets.audio import AudioAsset, AudioAssetParams


class ElevenLabsSpeechSynthesizer(BaseModel):
    """Speech synthesizer for ElevenLabs."""

    provider: ClassVar[str] = "elevenlabs"
    """Provider name for ElevenLabs."""

    api_key: str | None = None
    """API key for ElevenLabs."""

    voice_id: str
    """Voice ID for ElevenLabs."""

    voice_stability: Annotated[float, Field(ge=0, le=1)] = 0.5
    """Voice stability for the synthesized speech. It ranges from 0 to 1. Default is 0.5."""

    voice_similarity_boost: Annotated[float, Field(ge=0, le=1)] = 0.5
    """Voice similarity boost for the synthesized speech. It ranges from 0 to 1. Default is 0.5."""

    voice_style: Annotated[float, Field(ge=0, le=1)] = 0.5
    """Voice style for the synthesized speech. It ranges from 0 to 1. Default is 0.5."""

    voice_speaker_boost: bool = True
    """Voice speaker boost for the synthesized speech. Default is True."""

    language_code: LanguageAlpha2 = Field(default_factory=lambda: LanguageAlpha2("en"))
    """Language code of the text to synthesize. If not provided, it defaults to "en".

    Check the ElevenLabs API documentation for the list of supported languages by model.
    https://help.elevenlabs.io/hc/en-us/articles/17883183930129-What-models-do-you-offer-and-what-is-the-difference-between-them
    """

    model: Literal[
        "eleven_turbo_v2_5",
        "eleven_turbo_v2",
        "eleven_multilingual_v2",
        "eleven_monolingual_v1",
        "eleven_multilingual_v1",
    ] = "eleven_multilingual_v2"
    """Model ID for ElevenLabs."""

    timeout: int = 120
    """Timeout for the HTTP request in seconds."""

    def synthesize(
        self, texts: Sequence[str], *, audio_params: AudioAssetParams | None = None, **kwargs: Any
    ) -> list[AudioAsset]:
        """
        Synthesizes the given texts into audio assets using the ElevenLabs API.

        :param texts: List of texts to synthesize.
        :param audio_params: Audio parameters for the synthesized audio assets.
        :param kwargs: Additional keyword arguments.
        :return: List of synthesized audio assets.
        """
        assets = []
        previous_request_ids = []

        for i, text in enumerate(texts):
            is_first = i == 0
            is_last = i == len(texts) - 1
            response = self._fetch_speech_synthesis(
                text=text,
                previous_request_ids=previous_request_ids[-3:],
                previous_text=None if is_first else " ".join(texts[:i]),
                next_text=None if is_last else " ".join(texts[i + 1 :]),
            )
            previous_request_ids.append(response.headers["request-id"])
            duration = AudioSegment.from_file(io.BytesIO(response.content), format="mp3").duration_seconds
            asset = AudioAsset.from_data(
                response.content,
                params=audio_params if audio_params is not None else {},
                mime_type="audio/mpeg",
                duration=duration,
                sample_rate=44100,
                sample_width=128,
                channels=1,
            )
            assets.append(asset)

        return assets

    def _fetch_speech_synthesis(
        self,
        text: str,
        previous_request_ids: Sequence[str],
        previous_text: str | None = None,
        next_text: str | None = None,
    ) -> requests.Response:
        """
        Fetches the speech synthesis from the ElevenLabs API.
        """
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream",
            json={
                "text": text,
                "model_id": self.model,
                "previous_request_ids": previous_request_ids,
                "previous_text": previous_text,
                "next_text": next_text,
                "voice_settings": {
                    "stability": self.voice_stability,
                    "similarity_boost": self.voice_similarity_boost,
                    "style": self.voice_style,
                    "use_speaker_boost": self.voice_speaker_boost,
                },
            },
            headers={"xi-api-key": self.api_key or os.getenv("ELEVENLABS_API_KEY", "")},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response
