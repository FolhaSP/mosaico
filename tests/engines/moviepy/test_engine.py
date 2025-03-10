from pathlib import Path

import pytest

from mosaico.exceptions import AssetNotFoundError, EmptyTrackError
from mosaico.rendering.engines.moviepy.engine import MoviepyRenderingEngine, _guess_codec_from_file_path


@pytest.fixture
def rendering_engine():
    return MoviepyRenderingEngine()


def test_guess_codec_from_file_path():
    assert _guess_codec_from_file_path(Path("test.mp4")) == "libx264"
    assert _guess_codec_from_file_path(Path("test.avi")) == "rawvideo"
    assert _guess_codec_from_file_path(Path("test.ogv")) == "libvorbis"
    assert _guess_codec_from_file_path(Path("test.webm")) == "libvpx"
    assert _guess_codec_from_file_path(Path("test.unknown")) is None


def test_engine_initialization(rendering_engine):
    assert "audio" in rendering_engine.clip_renderers
    assert "image" in rendering_engine.clip_renderers
    assert "text" in rendering_engine.clip_renderers
    assert "subtitle" in rendering_engine.clip_renderers

    assert "zoom_in" in rendering_engine.effect_adapters
    assert "fade_out" in rendering_engine.effect_adapters
    assert "pan_center" in rendering_engine.effect_adapters


def test_render_empty_track(rendering_engine, empty_track, asset_map, rendering_options):
    with pytest.raises(EmptyTrackError):
        rendering_engine.render_track(empty_track, asset_map, rendering_options)


def test_asset_not_found(rendering_engine, track, rendering_options):
    with pytest.raises(AssetNotFoundError):
        rendering_engine.render_track(track, {}, rendering_options)


def test_render_project_invalid_output_directory(project):
    engine = MoviepyRenderingEngine()

    with pytest.raises(FileNotFoundError):
        engine.render_project(project, "/non/existent/directory/output.mp4")


def test_render_project_file_exists(tmp_path, project):
    engine = MoviepyRenderingEngine()

    # Create output file
    output_path = tmp_path / "output.mp4"
    output_path.write_text("")

    with pytest.raises(FileExistsError):
        engine.render_project(project, output_path)


def test_render_project_invalid_extension(project):
    engine = MoviepyRenderingEngine()

    with pytest.raises(ValueError, match=r"Output file must be an '.mp4' file"):
        engine.render_project(project, "output.wrong")


def test_mismatching_codec_and_extension(tmp_path, project):
    engine = MoviepyRenderingEngine()
    output_file = tmp_path / "output.mp4"
    tmp_path.mkdir(exist_ok=True)

    with pytest.raises(ValueError, match="Output file must be an '.avi' file."):
        engine.render_project(project, output_file.as_posix(), codec="rawvideo")
