from pathlib import Path

import pytest

from mosaico.audio_transcribers.transcription import Transcription


@pytest.fixture()
def srt_file_content(fixtures_dir: Path) -> str:
    return (fixtures_dir / "subtitles.srt").read_text()


def test_from_srt(srt_file_content) -> None:
    transcription = Transcription.from_srt(srt_file_content)
    assert len(transcription.words) == 71
    assert transcription.words[0].start_time == 0
    assert transcription.words[0].text == "Welcome"
    assert transcription.words[-1].end_time == 40
    assert transcription.words[-1].text == "videos!"


def test_to_srt(srt_file_content) -> None:
    transcription = Transcription.from_srt(srt_file_content)
    generated_srt = transcription.to_srt()
    assert generated_srt.startswith("1\n00:00:00")
    assert generated_srt.endswith("00:00:40,000\nvideos!\n")
