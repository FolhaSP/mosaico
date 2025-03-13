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
                    "content": textwrap.dedent("""
                        ## Task Description
                        I need you to correct an SRT subtitle file based on the original text. The current transcription contains errors or discrepancies compared to the original text. Your task is to align the transcription with the original text while preserving all the timing information.

                        ## Requirements
                        1. Keep all timestamp data exactly as it appears in the original SRT file.
                        2. Replace the transcribed text with the corresponding text from the original document.
                        3. Maintain the same number of subtitle entries/segments.
                        4. Follow the exact wording of the original text - no paraphrasing or summarizing.
                        5. Preserve all paragraph breaks and sentence structures from the original text.
                        6. Match the original text's capitalization, punctuation, and spelling.

                        ## Input Format
                        I will provide:
                        1. The original text (the accurate version that should appear in the subtitles)
                        2. The current SRT file content (with timing information that must be preserved)

                        ## Expected Output
                        An SRT file that:
                        - Contains the exact same number of entries as the original SRT
                        - Preserves all timestamp information (start and end times) from the original SRT
                        - Contains text that matches the original document's words exactly
                        - Maintains proper SRT formatting (sequential numbering, timestamps, and blank lines between entries)

                        ## Example
                        **Original Text:**
                        "Welcome to our presentation on climate change. Today, we'll discuss the latest research findings and their implications for global policy."

                        **Current SRT:**
                        ```
                        1
                        00:00:01,000 --> 00:00:03,500
                        Welcome to our presentation about climate change.

                        2
                        00:00:03,600 --> 00:00:08,200
                        Today, we will talk about the newest research and what it means for worldwide policy.
                        ```

                        **Corrected SRT:**
                        ```
                        1
                        00:00:01,000 --> 00:00:03,500
                        Welcome to our presentation on climate change.

                        2
                        00:00:03,600 --> 00:00:08,200
                        Today, we'll discuss the latest research findings and their implications for global policy.
                        ```

                        ## Additional Guidelines
                        - If the original text is longer than what can fit in the existing SRT segments, prioritize maintaining accurate timestamps and distribute the text appropriately across segments.
                        - If the original text is shorter, ensure all segments still contain appropriate content - don't leave any segments empty.
                        - Ensure special characters, formatting, and emphasis from the original text are preserved.
                        - Make sure line breaks within a subtitle segment are appropriate for readability.

                        Please provide both the original text and the current SRT file, and I'll correct the transcription accordingly.
                        """),
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
                        """).strip(),
                },
            ],
            response_model=str,
            **model_params,
        )

        return Transcription.from_srt(fixed_transcription)
