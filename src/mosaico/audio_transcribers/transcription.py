from __future__ import annotations

from pydantic import BaseModel
from pydantic.config import ConfigDict
from pydantic.types import NonNegativeFloat
from typing_extensions import Self


class TranscriptionWord(BaseModel):
    """A word in a transcription."""

    start_time: NonNegativeFloat
    """The start time of the word in seconds."""

    end_time: NonNegativeFloat
    """The end time of the word in seconds."""

    text: str
    """The text of the word."""

    model_config = ConfigDict(validate_assignment=True)


class Transcription(BaseModel):
    """A transcription of an audio asset."""

    words: list[TranscriptionWord]
    """The words in the transcription."""

    @property
    def duration(self) -> float:
        """The duration of the transcription in seconds."""
        return self.words[-1].end_time - self.words[0].start_time

    @classmethod
    def from_srt(cls, srt: str) -> Self:
        """
        Create a transcription from an SRT string.

        :param srt: The SRT string.
        :return: The transcription.
        """
        lines = srt.strip().split("\n")
        words = []
        for i in range(1, len(lines), 4):
            start_time, end_time = lines[i].split(" --> ")
            word = TranscriptionWord(
                start_time=float(start_time.replace(",", ".")),
                end_time=float(end_time.replace(",", ".")),
                text=lines[i + 1],
            )
            words.append(word)
        return cls(words=words)

    @classmethod
    def from_vtt(cls, vtt: str) -> Self:
        """
        Create a transcription from a WebVTT string.

        :param vtt: The WebVTT string.
        :return: The transcription.
        """
        lines = vtt.strip().split("\n")
        if not lines[0].strip().upper() == "WEBVTT":
            raise ValueError("Not a valid WebVTT file.")
        words = []
        for i in range(1, len(lines), 4):
            start_time, end_time = lines[i + 1].split(" --> ")
            word = TranscriptionWord(start_time=float(start_time), end_time=float(end_time), text=lines[i + 2])
            words.append(word)
        return cls(words=words)

    def as_vtt(self) -> str:
        """Return the transcription as a WebVTT string."""
        lines = ["WEBVTT", ""]
        for i, word in enumerate(self.words):
            lines.append(f"{i + 1}")
            lines.append(f"{word.start_time:.3f} --> {word.end_time:.3f}")
            lines.append(word.text)
            lines.append("")
        return "\n".join(lines)
