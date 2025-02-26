import io
from pathlib import Path

import pytest
from pydub import AudioSegment
from pytest_mock import MockerFixture

from mosaico.assets.audio import AudioAsset, AudioInfo


@pytest.fixture
def sample_audio_data():
    # Create a simple test audio in memory (1 second of silence)
    audio = AudioSegment.silent(duration=1000)  # 1 second
    audio_byte_arr = io.BytesIO()
    audio.export(audio_byte_arr, format="mp3")
    return audio_byte_arr.getvalue()


@pytest.fixture
def sample_audio_path(tmp_path, sample_audio_data):
    # Create a temporary audio file
    audio_path = tmp_path / "test_audio.mp3"
    with open(audio_path, "wb") as f:
        f.write(sample_audio_data)
    return audio_path


def test_audio_asset_from_data(sample_audio_data):
    # Test creating AudioAsset from raw data
    audio_asset = AudioAsset.from_data(sample_audio_data)

    assert audio_asset.type == "audio"
    assert audio_asset.duration > 0
    assert audio_asset.sample_rate > 0
    assert audio_asset.sample_width >= 0
    assert audio_asset.channels > 0
    assert audio_asset.data == sample_audio_data


def test_audio_asset_from_data_with_explicit_params(sample_audio_data: bytes, mocker: MockerFixture):
    # Test creating AudioAsset with explicitly provided parameters
    audio_info = AudioInfo(duration=2.0, sample_rate=44100, sample_width=2, channels=2)
    audio_asset = AudioAsset.from_data(sample_audio_data, info=audio_info)
    load_info_spy = mocker.spy(AudioAsset, "_load_info")

    load_info_spy.assert_not_called()
    assert audio_asset.duration == 2.0
    assert audio_asset.sample_rate == 44100
    assert audio_asset.sample_width == 2
    assert audio_asset.channels == 2
    assert audio_asset.data == sample_audio_data


def test_audio_asset_from_path(sample_audio_path):
    # Test creating AudioAsset from file path
    audio_asset = AudioAsset.from_path(sample_audio_path)

    assert audio_asset.type == "audio"
    assert audio_asset.duration > 0
    assert audio_asset.sample_rate > 0
    assert audio_asset.sample_width >= 0
    assert audio_asset.channels > 0

    with open(sample_audio_path, "rb") as f:
        expected_data = f.read()

    assert audio_asset.to_bytes() == expected_data


def test_audio_asset_from_path_with_pathlib(sample_audio_path):
    # Test creating AudioAsset using Path object
    path_obj = Path(sample_audio_path)
    audio_asset = AudioAsset.from_path(path_obj)

    assert audio_asset.type == "audio"
    assert audio_asset.duration > 0
    assert audio_asset.sample_rate > 0


def test_audio_asset_slice(sample_audio_data):
    # Test slicing audio asset
    audio_asset = AudioAsset.from_data(sample_audio_data)
    sliced_asset = audio_asset.slice(0.0, 0.5)  # Slice first half second

    assert sliced_asset.type == "audio"
    assert sliced_asset.duration <= audio_asset.duration
    assert sliced_asset.sample_rate == audio_asset.sample_rate
    assert sliced_asset.sample_width == audio_asset.sample_width
    assert sliced_asset.channels == audio_asset.channels


def test_audio_asset_from_invalid_data():
    # Test handling invalid audio data
    with pytest.raises(Exception):
        asset = AudioAsset.from_data(b"invalid audio data")
        asset.duration


def test_audio_asset_params_default_values(sample_audio_data):
    # Test default parameter values
    audio_asset = AudioAsset.from_data(sample_audio_data)

    assert audio_asset.params.volume == 1.0
    assert audio_asset.params.crop is None


def test_audio_asset_with_metadata(sample_audio_data):
    # Test creating AudioAsset with metadata
    metadata = {"artist": "Test Artist", "title": "Test Track"}
    audio_asset = AudioAsset.from_data(sample_audio_data, metadata=metadata)

    assert audio_asset.metadata == metadata


def test_slice_out_of_bounds(sample_audio_data):
    # Test slicing with out of bounds values
    audio_asset = AudioAsset.from_data(sample_audio_data)

    # Slice beyond audio duration
    sliced_asset = audio_asset.slice(0.0, 10.0)
    assert sliced_asset.duration <= audio_asset.duration


def test_audio_asset_params_modification(sample_audio_data):
    # Test modifying audio parameters
    audio_asset = AudioAsset.from_data(sample_audio_data)

    audio_asset.params.volume = 0.5
    assert audio_asset.params.volume == 0.5

    audio_asset.params.crop = (0, 500)
    assert audio_asset.params.crop == (0, 500)
