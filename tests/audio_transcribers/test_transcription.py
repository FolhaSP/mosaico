from pathlib import Path

from mosaico.audio_transcribers.transcription import Transcription


def test_from_srt(fixtures_dir: Path) -> None:
    srt_file = fixtures_dir / "example.srt"
    transcription = Transcription.from_srt(srt_file.read_text())
    assert len(transcription.words) == 71
    assert transcription.words[0].start_time == 0
    assert transcription.words[0].text == "Welcome"
    assert transcription.words[-1].end_time == 40
    assert transcription.words[-1].text == "videos!"
