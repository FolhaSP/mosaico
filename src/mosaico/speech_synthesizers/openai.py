import io
from collections.abc import Sequence
from typing import Annotated, Any, ClassVar, Literal

from openai import OpenAI
from pydantic import BaseModel
from pydantic.fields import Field, PrivateAttr
from pydantic.functional_validators import model_validator
from pydantic.types import PositiveInt
from pydub import AudioSegment
from typing_extensions import Self

from mosaico.assets.audio import AudioAsset, AudioAssetParams


class OpenAISpeechSynthesizer(BaseModel):
    """Speech synthesizer using OpenAI's API."""

    provider: ClassVar[str] = "openai"
    """Provider name for OpenAI."""

    api_key: str | None = None
    """API key for OpenAI's API."""

    base_url: str | None = None
    """Base URL for OpenAI's API."""

    model: Literal["tts-1", "tts-1-hd"] = "tts-1"
    """Model to use for speech synthesis."""

    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "alloy"
    """Voice to use for speech synthesis."""

    speed: Annotated[float, Field(ge=0.25, le=4)] = 1.0
    """Speed of speech synthesis."""

    timeout: PositiveInt = 120
    """Timeout for speech synthesis in seconds."""

    _client: Any = PrivateAttr(default=None)
    """The OpenAI client."""

    @model_validator(mode="after")
    def _set_client(self) -> Self:
        """
        Set the OpenAI client.
        """
        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)
        return self

    def synthesize(
        self, texts: Sequence[str], *, audio_params: AudioAssetParams | None = None, **kwargs: Any
    ) -> list[AudioAsset]:
        """
        Synthesize speech from texts using OpenAI's API.

        :param texts: Texts to synthesize.
        :param audio_params: Parameters for the audio asset.
        :param kwargs: Additional parameters for the OpenAI API.
        :return: List of audio assets.
        """
        assets = []

        for text in texts:
            response = self._client.audio.speech.create(
                input=text, model=self.model, voice=self.voice, response_format="mp3", speed=self.speed, **kwargs
            )
            segment = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")
            assets.append(
                AudioAsset.from_data(
                    response.content,
                    params=audio_params if audio_params is not None else {},
                    duration=segment.duration,
                    sample_rate=segment.frame_rate,
                    sample_width=segment.sample_width,
                    channels=segment.channels,
                    mime_type="audio/mpeg",
                )
            )

        return assets