from pathlib import Path

import pytest

from mosaico.video.rendering import _guess_codec_from_file_path, render_video


# Dummy classes to simulate a VideoProject and minimal dependencies.
class DummyConfig:
    title = "TestVideo"
    resolution = (640, 480)
    fps = 24


class DummyProject:
    def __init__(self):
        self.config = DummyConfig()
        self.duration = 10
        self.timeline = []  # Keeping it empty, no events needed for these tests.

    def get_asset(self, asset_id):
        # Not used in our tests since timeline is empty.
        return None


# Dummy composite video clip to bypass actual Moviepy processing.
class DummyCompositeVideoClip:
    def __init__(self, clips, size):
        self.clips = clips
        self.size = size

    def with_fps(self, fps):
        return self

    def with_duration(self, duration):
        return self

    def with_audio(self, audio):
        return self

    def write_videofile(self, path, **kwargs):
        # Fake write; do nothing.
        pass

    def close(self):
        pass


@pytest.fixture(autouse=True)
def patch_moviepy(monkeypatch):
    # Patch CompositeVideoClip used in render_video with our dummy clip.
    monkeypatch.setattr("mosaico.video.rendering.CompositeVideoClip", DummyCompositeVideoClip)


@pytest.fixture
def dummy_project():
    return DummyProject()


def test_output_directory_not_exists(tmp_path, dummy_project):
    # Create a path that is inside a non-existent directory.
    non_existing_dir = tmp_path / "non_existing_folder"
    output_file = non_existing_dir / "output.mp4"

    with pytest.raises(FileNotFoundError, match="Output directory does not exist"):
        render_video(dummy_project, output_file.as_posix())


def test_file_already_exists(tmp_path, dummy_project):
    output_file = tmp_path / "output.mp4"
    output_file.touch()

    with pytest.raises(FileExistsError, match="Output file already exists"):
        render_video(dummy_project, output_file.as_posix(), overwrite=False)


def test_mismatching_codec_and_extension(tmp_path, dummy_project):
    output_file = tmp_path / "output.mp4"
    tmp_path.mkdir(exist_ok=True)

    with pytest.raises(ValueError, match="Output file must be an '.avi' file."):
        render_video(dummy_project, output_file.as_posix(), codec="rawvideo")


def test_guessing_codec_from_file_extension(tmp_path):
    output_file = tmp_path / "output.avi"
    output_codec = _guess_codec_from_file_path(output_file)

    assert output_codec == "rawvideo"  # there are 3 alternatives, it should get the first one.


def test_successful_rendering(tmp_path, dummy_project):
    output_file = tmp_path / "output.mp4"
    returned_path = render_video(dummy_project, output_file.as_posix(), overwrite=False)

    assert Path(returned_path) == output_file.resolve()
    assert not output_file.exists()
