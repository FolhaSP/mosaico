import io
from collections.abc import Sequence
from typing import Annotated, Any, ClassVar, Literal

from pydantic import BaseModel
from pydantic.fields import Field, PrivateAttr
from pydantic.functional_validators import model_validator
from pydantic.types import PositiveInt
from pydub import AudioSegment
from typing_extensions import Self

from mosaico.assets.audio import AudioAsset, AudioAssetParams, AudioInfo


OpenAITTSVoice = Literal["alloy", "ash", "ballad", "echo", "coral", "fable", "onyx", "nova", "sage", "shimmer", "verse"]
"""OpenAI's text-to-speech available voices."""


class OpenAISpeechSynthesizer(BaseModel):
    """Speech synthesizer using OpenAI's API."""

    provider: ClassVar[str] = "openai"
    """Provider name for OpenAI."""

    api_key: str | None = None
    """API key for OpenAI's API."""

    base_url: str | None = None
    """Base URL for OpenAI's API."""

    model: Literal["gpt-4o-mini-tts", "tts-1", "tts-1-hd"] = "gpt-4o-mini-tts"
    """Model to use for speech synthesis."""

    voice: OpenAITTSVoice = "alloy"
    """Voice to use for speech synthesis."""

    speed: Annotated[float, Field(ge=0.25, le=4)] = 1.0
    """Speed of speech synthesis."""

    timeout: PositiveInt = 120
    """Timeout for speech synthesis in seconds."""

    instructions: str | None = None
    """Instructions passed to the model. Valid only when the model is from the GPT-4o family or higher."""

    _client: Any = PrivateAttr(default=None)
    """The OpenAI client."""

    @model_validator(mode="after")
    def _validate_model_supports_instructions(self) -> Self:
        """
        Validates whether the selected model supports instructions.
        """
        if self.instructions and self.model.startswith("tts-"):
            raise ValueError("`instructions` cannot be set when model is not from the GPT-4o family or higher.")
        return self

    @model_validator(mode="after")
    def _set_client(self) -> Self:
        """
        Set the OpenAI client.
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("The 'openai' package is required for using the OpenAISpeechSynthesizer.")
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

        model = kwargs.pop("model", self.model)
        instructions = kwargs.pop("instructions", self.instructions)

        if instructions and model.startswith("tts-"):
            raise ValueError("`instructions` cannot be set when model is not from the GPT-4o family or higher.")

        for text in texts:
            response = self._client.audio.speech.create(
                input=text,
                model=model,
                instructions=instructions,
                voice=kwargs.pop("voice", self.voice),
                speed=kwargs.pop("speed", self.speed),
                response_format="mp3",
                **kwargs,
            )
            segment = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")
            assets.append(
                AudioAsset.from_data(
                    response.content,
                    params=audio_params if audio_params is not None else {},
                    mime_type="audio/mpeg",
                    info=AudioInfo(
                        duration=segment.duration_seconds,
                        sample_rate=segment.frame_rate,
                        sample_width=segment.sample_width,
                        channels=segment.channels,
                    ),
                )
            )

        return assets
