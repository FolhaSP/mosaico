from __future__ import annotations

from pydantic import BaseModel
from pydantic.config import ConfigDict
from pydantic.types import NonNegativeFloat


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
    def from_srt(cls, srt: str) -> Transcription:
        """
        Create a transcription from an SRT string.

        :param srt: The SRT string.
        :return: The transcription.
        """
        lines = srt.strip().split("\n")
        words = []
        for i in range(0, len(lines)):
            if not " --> " in lines[i]:
                continue
            start_time, end_time = map(_extract_time_from_string, lines[i].split(" --> "))
            line_words = lines[i + 1].split(" ")
            line_duration = end_time - start_time
            current_start_time = start_time
            current_end_time = None
            for word_index, line_word in enumerate(line_words):
                if current_end_time is None or word_index < len(line_words) - 1:
                    current_end_time = round(current_start_time + line_duration / len(line_words), 3)
                else:
                    current_end_time = end_time
                word = TranscriptionWord(start_time=current_start_time, end_time=current_end_time, text=line_word)
                words.append(word)
                current_start_time = current_end_time
        return cls(words=words)

    def to_srt(self) -> str:
        """Return the transcription as an SRT string."""
        lines = []
        for i, word in enumerate(self.words):
            lines.append(f"{i + 1}")
            lines.append(f"{word.start_time:.3f} --> {word.end_time:.3f}")
            lines.append(word.text)
            lines.append("")
        return "\n".join(lines)


def _extract_time_from_string(time_str: str) -> float:
    """Extract time from a string in the format HH:MM:SS.mmm."""
    hours, minutes, seconds = time_str.replace(",", ".").split(":")
    return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
