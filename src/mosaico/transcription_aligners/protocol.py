from typing import Protocol, runtime_checkable

from mosaico.audio_transcribers.transcription import Transcription


@runtime_checkable
class TranscriptionAligner(Protocol):
    """
    Protocol for transcription aligners.

    This protocol defines the interface for aligning transcriptions with their original text.
    """

    def align(self, transcription: Transcription, original_text: str) -> Transcription:
        """
        Aligns the given transcription with the original text.

        :param transcription: The transcription to align.
        :param original_text: The original text to align with.
        :return: The aligned transcription.
        """
        ...
