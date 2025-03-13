import textwrap
from typing import Any

import instructor
import litellm

from mosaico.audio_transcribers.transcription import Transcription
from mosaico.transcription_aligners.protocol import TranscriptionAligner


class GenAITranscriptionAligner(TranscriptionAligner):
    """Aligns transcription with original text using generative AI."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        model_params: dict[str, Any] | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 120,
    ) -> None:
        self.model = model
        self.model_params = model_params
        self.client = instructor.from_litellm(litellm.completion, api_key=api_key, base_url=base_url, timeout=timeout)

    def align(self, transcription: Transcription, original_text: str) -> Transcription:
        """
        Aligns a transcription using generative AI based on an original text.

        :param transcription: Transcription with timing information.
        :param original_text: Original script text.
        :return: A new transcription with aligned text and timing.
        """
        model_params = self.model_params or {"temperature": 0}
        fixed_transcription = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant and your job is to fix "
                        "transcribed words according to the original text"
                    ),
                },
                {
                    "role": "user",
                    "content": textwrap.dedent(f"""
                        Fix this transcription SRT based on the original text of the audio.

                        The transcription SRT:

                        <transcription>
                        {transcription.to_srt()}
                        </transcription>

                        The original audio text:

                        <original_text>
                        {original_text}
                        </original_text>

                        Keep the original text as it is, with it's original punctuation and words.
                        Answer only with the fixed transcription SRT with the original timing.
                        """).strip(),
                },
            ],
            response_model=str,
            **model_params,
        )

        return Transcription.from_srt(fixed_transcription)
