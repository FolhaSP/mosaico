from collections.abc import Sequence
from typing import Any, ClassVar
from unittest.mock import patch

import pytest
import yaml

from mosaico.assets.audio import AudioAsset, AudioAssetParams
from mosaico.assets.reference import AssetReference
from mosaico.assets.subtitle import SubtitleAsset
from mosaico.assets.text import TextAsset, TextAssetParams
from mosaico.audio_transcribers.transcription import Transcription, TranscriptionWord
from mosaico.media import Media
from mosaico.scene import Scene
from mosaico.script_generators.script import ShootingScript, Shot
from mosaico.video.project import VideoProject, VideoProjectConfig, _group_transcript_into_sentences
from mosaico.video.timeline import Timeline


def test_default_config() -> None:
    config = VideoProjectConfig()
    assert config.title == "Untitled Project"
    assert config.version == 1
    assert config.resolution == (1920, 1080)
    assert config.fps == 30


def test_add_single_asset() -> None:
    asset = TextAsset.from_data("test", id="asset_1")
    project = VideoProject().add_assets(asset)
    assert "asset_1" in project.assets
    assert project.assets["asset_1"].id == asset.id
    assert project.assets["asset_1"].data == "test"


def test_add_single_dict_asset() -> None:
    asset = {"id": "asset_1", "type": "text", "data": "test"}
    project = VideoProject().add_assets(asset)
    assert "asset_1" in project.assets
    assert project.assets["asset_1"].id == asset["id"]
    assert project.assets["asset_1"].data == "test"


def test_add_multiple_assets() -> None:
    assets = [TextAsset.from_data("test", id="asset_1"), TextAsset.from_data("test", id="asset_2")]
    project = VideoProject().add_assets(assets)
    assert "asset_1" in project.assets
    assert project.assets["asset_1"].id == assets[0].id
    assert project.assets["asset_1"].data == "test"
    assert "asset_2" in project.assets
    assert project.assets["asset_2"].id == assets[1].id
    assert project.assets["asset_2"].data == "test"


def test_add_multiple_dict_assets() -> None:
    assets = [{"id": "asset_1", "type": "text", "data": "test"}, {"id": "asset_2", "type": "text", "data": "test"}]
    project = VideoProject().add_assets(assets)
    assert "asset_1" in project.assets
    assert project.assets["asset_1"].id == assets[0]["id"]
    assert project.assets["asset_1"].data == "test"
    assert "asset_2" in project.assets
    assert project.assets["asset_2"].id == assets[1]["id"]
    assert project.assets["asset_2"].data == "test"


def test_add_timeline_events_single_asset_reference():
    asset = TextAsset.from_data("test", id="asset1")
    event = AssetReference.from_asset(asset, start_time=0, end_time=10)
    project = VideoProject().add_assets(asset).add_timeline_events(event)
    assert project.timeline == Timeline().add_events([event])


def test_add_timeline_events_single_scene():
    asset = TextAsset.from_data("test", id="asset1")
    ref = AssetReference.from_asset(asset, start_time=0, end_time=10)
    scene = Scene(asset_references=[ref])
    project = VideoProject().add_assets(asset).add_timeline_events(scene)
    assert project.timeline == Timeline([scene])


def test_add_timeline_events_multiple_asset_references():
    asset1 = TextAsset.from_data("test", id="asset1")
    asset2 = TextAsset.from_data("test", id="asset2")
    event1 = AssetReference.from_asset(asset1, start_time=0, end_time=10)
    event2 = AssetReference.from_asset(asset2, start_time=0, end_time=20)
    project = VideoProject().add_assets([asset1, asset2]).add_timeline_events([event1, event2])
    assert project.timeline == Timeline().add_events([event1, event2])


def test_add_timeline_events_multiple_scenes():
    asset1 = TextAsset.from_data("test", id="asset1")
    asset2 = TextAsset.from_data("test", id="asset2")
    ref1 = AssetReference.from_asset(asset1, start_time=0, end_time=10)
    ref2 = AssetReference.from_asset(asset2, start_time=0, end_time=20)
    scene1 = Scene(asset_references=[ref1])
    scene2 = Scene(asset_references=[ref2])
    project = VideoProject().add_assets([asset1, asset2]).add_timeline_events([scene1, scene2])
    assert project.timeline == Timeline().add_events([scene1, scene2])


def test_add_timeline_events_single_dict_asset_reference():
    asset = TextAsset.from_data("test", id="asset1")
    event = {"asset_id": "asset1", "asset_type": "text", "start_time": 0, "end_time": 10}
    project = VideoProject().add_assets(asset).add_timeline_events(event)
    assert project.timeline == Timeline().add_events([AssetReference.from_dict(event)])


def test_add_timeline_events_single_dict_scene():
    asset = TextAsset.from_data("test", id="asset1")
    ref = AssetReference.from_asset(asset, start_time=0, end_time=10)
    scene = {"asset_references": [ref]}
    project = VideoProject().add_assets(asset).add_timeline_events(scene)
    assert project.timeline == Timeline().add_events([Scene.from_dict(scene)])


def test_add_timeline_events_multiple_dict_asset_references():
    asset1 = TextAsset.from_data("test", id="asset1")
    asset2 = TextAsset.from_data("test", id="asset2")
    event1 = {"asset_id": "asset1", "asset_type": "text", "start_time": 0, "end_time": 10}
    event2 = {"asset_id": "asset2", "asset_type": "text", "start_time": 0, "end_time": 20}
    project = VideoProject().add_assets([asset1, asset2]).add_timeline_events([event1, event2])
    assert project.timeline == Timeline().add_events(
        [AssetReference.from_dict(event1), AssetReference.from_dict(event2)]
    )


def test_add_timeline_events_multiple_dict_scenes():
    asset1 = TextAsset.from_data("test", id="asset1")
    asset2 = TextAsset.from_data("test", id="asset2")
    ref1 = AssetReference.from_asset(asset1, start_time=0, end_time=10)
    ref2 = AssetReference.from_asset(asset2, start_time=0, end_time=20)
    scene1 = {"asset_references": [ref1]}
    scene2 = {"asset_references": [ref2]}
    project = VideoProject().add_assets([asset1, asset2]).add_timeline_events([scene1, scene2])
    assert project.timeline == Timeline().add_events([Scene.model_validate(scene1), Scene.model_validate(scene2)])


def test_add_timeline_events_without_assets() -> None:
    event = AssetReference(asset_id="test", asset_type="text", start_time=0, end_time=10)
    with pytest.raises(IndexError, match="Asset with ID 'test' not found in project assets"):
        VideoProject().add_timeline_events(event)


def test_duration() -> None:
    timeline_event_1 = AssetReference(asset_id="test_1", asset_type="text", start_time=0, end_time=10)
    timeline_event_2 = AssetReference(asset_id="test_2", asset_type="text", start_time=0, end_time=20)
    assets = [
        TextAsset.from_data("test 1", id="test_1"),
        TextAsset.from_data("test 2", id="test_2"),
    ]
    project = VideoProject().add_assets(assets).add_timeline_events([timeline_event_1, timeline_event_2])
    assert project.duration == 20


def test_get_asset() -> None:
    asset = TextAsset.from_data("test", id="asset1")
    project = VideoProject().add_assets(asset)
    assert project.get_asset("asset1") == asset
    with pytest.raises(KeyError, match="Asset with ID 'nonexistent' not found in the project assets"):
        project.get_asset("nonexistent")


def test_iter_timeline() -> None:
    asset1 = TextAsset.from_data("test", id="asset1")
    asset2 = TextAsset.from_data("test", id="asset2")
    ref1 = AssetReference.from_asset(asset1, start_time=0, end_time=10)
    ref2 = AssetReference.from_asset(asset2, start_time=0, end_time=20)
    scene1 = Scene(asset_references=[ref1])
    scene2 = Scene(asset_references=[ref2])
    project = VideoProject().add_assets([asset1, asset2]).add_timeline_events([scene1, scene2])
    assert project.timeline == Timeline().add_events([scene1, scene2])


@pytest.fixture
def mock_project_file(tmp_path):
    project_data = {
        "config": {"title": "Test Project", "version": 1, "resolution": (1920, 1080), "fps": 30},
        "assets": {"asset1": {"type": "text", "data": "test", "id": "asset1"}},
        "timeline": [{"asset_id": "asset1", "asset_type": "text", "start_time": 0, "end_time": 10}],
    }
    project_file = tmp_path / "project.yaml"
    project_file.write_text(yaml.safe_dump(project_data))
    return project_file


def test_from_file_success(mock_project_file):
    project = VideoProject.from_file(mock_project_file)
    assert project.config.title == "Test Project"
    assert project.config.resolution == (1920, 1080)
    assert project.config.fps == 30
    assert project.assets == {"asset1": TextAsset.from_data("test", id="asset1")}
    assert project.timeline == Timeline().add_events(
        [AssetReference(asset_id="asset1", asset_type="text", start_time=0, end_time=10)]
    )


def test_from_file_invalid_path():
    with pytest.raises(FileNotFoundError):
        VideoProject.from_file("non_existent_file.yaml")


def test_to_file(mock_project_file, tmp_path):
    project = VideoProject.from_file(mock_project_file)
    project_file = tmp_path / "project.yaml"
    project.to_file(project_file)
    assert project_file.read_text() == mock_project_file.read_text()


class MockScriptGenerator:
    def generate(self, media: Sequence[Media], **kwargs: Any) -> ShootingScript:
        return ShootingScript(
            title="Test Script",
            description="This is a test script",
            shots=[
                Shot(
                    number=1,
                    description="Shot 1",
                    start_time=0,
                    end_time=5,
                    subtitle="Hello world",
                    media_id=media[0].id,
                ),
                Shot(
                    number=2,
                    description="Shot 2",
                    start_time=5,
                    end_time=10,
                    subtitle="This is a test",
                    media_id=media[1].id,
                ),
            ],
        )


class MockSpeechSynthesizer:
    provider: ClassVar[str] = "test"

    def synthesize(
        self, texts: Sequence[str], *, audio_params: AudioAssetParams | None = None, **kwargs: Any
    ) -> list[AudioAsset]:
        return [
            AudioAsset.from_data(
                "test_audio",
                id="test_audio",
                duration=len(text) * 0.1,
                sample_width=16,
                sample_rate=44100,
                channels=1,
                mime_type="audio/wav",
            )
            for text in texts
        ]


class MockAudioTranscriber:
    def transcribe(self, audio_asset: AudioAsset) -> Transcription:
        words = audio_asset.to_string().split()  # Assume audio.data is the text
        return Transcription(
            words=[
                TranscriptionWord(text=word, start_time=i * 0.5, end_time=(i + 1) * 0.5) for i, word in enumerate(words)
            ]
        )


# Subtitle Tests
@pytest.fixture
def sample_transcription():
    return Transcription(
        words=[
            TranscriptionWord(text="Hello", start_time=0.0, end_time=0.5),
            TranscriptionWord(text="world", start_time=0.5, end_time=1.0),
            TranscriptionWord(text="This", start_time=1.0, end_time=1.5),
            TranscriptionWord(text="is", start_time=1.5, end_time=2.0),
            TranscriptionWord(text="a", start_time=2.0, end_time=2.2),
            TranscriptionWord(text="test", start_time=2.2, end_time=2.5),
        ]
    )


def test_add_captions_basic(sample_transcription):
    project = VideoProject().add_captions(sample_transcription)

    # Verify assets were created
    subtitle_assets = [asset for asset in project.assets.values() if isinstance(asset, SubtitleAsset)]
    assert len(subtitle_assets) == 1

    # Verify timeline events
    subtitle_refs = [ref for ref in project.timeline if isinstance(project.assets[ref.asset_id], SubtitleAsset)]
    assert len(subtitle_refs) == 1
    assert subtitle_refs[0].start_time == 0.0
    assert subtitle_refs[0].end_time == 2.5


def test_add_captions_with_max_duration(sample_transcription):
    project = VideoProject().add_captions(sample_transcription, max_duration=1)

    # Should split into multiple subtitle assets/references
    subtitle_refs = [ref for ref in project.timeline if isinstance(project.assets[ref.asset_id], SubtitleAsset)]
    assert len(subtitle_refs) == 3

    # Verify timing of segments
    assert subtitle_refs[0].start_time == 0.0
    assert subtitle_refs[0].end_time == 1.0
    assert subtitle_refs[1].start_time == 1.0
    assert subtitle_refs[1].end_time == 2.0
    assert subtitle_refs[2].start_time == 2.0
    assert subtitle_refs[2].end_time == 2.5


def test_add_captions_with_params(sample_transcription):
    params = TextAssetParams(font_size=24, font_color="#FFFFFF")
    project = VideoProject().add_captions(sample_transcription, params=params)

    subtitle_refs = [ref for ref in project.timeline if ref.asset_type == "subtitle"]
    assert len(subtitle_refs) == 1

    # Verify params were applied
    assert subtitle_refs[0].asset_params.font_size == 24
    assert subtitle_refs[0].asset_params.font_color.as_hex().upper() == "#FFF"


@patch("mosaico.audio_transcribers.protocol.AudioTranscriber")
def test_add_captions_from_transcriber(mock_transcriber, sample_transcription):
    # Setup
    audio_asset = AudioAsset.from_data(
        "test_audio", id="audio1", duration=2.5, sample_rate=44100, sample_width=128, channels=1
    )
    mock_transcriber.transcribe.return_value = sample_transcription

    # Create project with audio in timeline
    scene = Scene(description="Test scene")
    ref = AssetReference.from_asset(audio_asset, start_time=0, end_time=2.5)
    scene = scene.add_asset_references(ref)

    project = VideoProject().add_assets(audio_asset).add_timeline_events(scene)

    # Add captions
    project = project.add_captions_from_transcriber(mock_transcriber)

    # Verify transcriber was called
    mock_transcriber.transcribe.assert_called_once_with(audio_asset)

    # Verify subtitles were added to scene
    scene = next(event for event in project.timeline if isinstance(event, Scene))
    subtitle_refs = [ref for ref in scene.asset_references if isinstance(project.assets[ref.asset_id], SubtitleAsset)]
    assert len(subtitle_refs) > 0


def test_from_script_generator():
    media = [
        Media.from_data("test1", id="1", mime_type="text/plain"),
        Media.from_data("test2", id="2", mime_type="text/plain"),
    ]

    project = VideoProject.from_script_generator(script_generator=MockScriptGenerator(), media=media)

    assert isinstance(project, VideoProject)
    assert len(project.timeline) == 2


def test_group_words_into_phrases():
    transcription = Transcription(
        words=[
            TranscriptionWord(text="Hello", start_time=0.0, end_time=0.5),
            TranscriptionWord(text="world", start_time=0.5, end_time=1.0),
            TranscriptionWord(text="This", start_time=1.0, end_time=1.5),
            TranscriptionWord(text="is", start_time=1.5, end_time=1.7),
            TranscriptionWord(text="a", start_time=1.7, end_time=1.8),
            TranscriptionWord(text="test", start_time=1.8, end_time=2.3),
            TranscriptionWord(text="with", start_time=2.3, end_time=2.6),
            TranscriptionWord(text="numbers", start_time=2.6, end_time=3.1),
            TranscriptionWord(text="123.45", start_time=3.1, end_time=3.6),
        ]
    )

    phrases = _group_transcript_into_sentences(transcription, max_duration=2.0)

    assert len(phrases) == 2
    assert " ".join(word.text for word in phrases[0]) == "Hello world This is a"
    assert " ".join(word.text for word in phrases[1]) == "test with numbers 123.45"


def test_group_words_into_phrases_with_numbers():
    transcription = Transcription(
        words=[
            TranscriptionWord(text="The", start_time=0.0, end_time=0.2),
            TranscriptionWord(text="number", start_time=0.2, end_time=0.5),
            TranscriptionWord(text="is", start_time=0.5, end_time=0.7),
            TranscriptionWord(text="123", start_time=0.7, end_time=1.0),
            TranscriptionWord(text=".", start_time=1.0, end_time=1.1),
            TranscriptionWord(text="45", start_time=1.1, end_time=1.4),
            TranscriptionWord(text="and", start_time=1.4, end_time=1.6),
            TranscriptionWord(text="6,789", start_time=1.6, end_time=2.0),
        ]
    )

    phrases = _group_transcript_into_sentences(transcription, max_duration=1.5)

    assert len(phrases) == 2
    assert " ".join(word.text for word in phrases[0]) == "The number is 123 . 45"
    assert " ".join(word.text for word in phrases[1]) == "and 6,789"


def test_with_subtitle_params_asset_reference() -> None:
    # Create a subtitle asset
    subtitle_asset = SubtitleAsset.from_data("test text", id="subtitle1")

    # Create project with timeline event
    event = AssetReference.from_asset(subtitle_asset, start_time=0, end_time=10)
    project = VideoProject().add_assets(subtitle_asset).add_timeline_events(event)

    # New subtitle params
    new_params = {"font_size": 24, "font_color": "#FFFFFF"}

    # Update subtitle params
    project = project.with_subtitle_params(new_params)

    # Check if params were updated
    assert project.timeline[0].asset_params.font_size == 24
    assert project.timeline[0].asset_params.font_color.as_hex().upper() == "#FFF"


def test_with_subtitle_params_scene() -> None:
    # Create subtitle assets
    subtitle1 = SubtitleAsset.from_data("test 1", id="subtitle1")
    subtitle2 = SubtitleAsset.from_data("test 2", id="subtitle2")

    # Create asset references
    ref1 = AssetReference.from_asset(subtitle1, start_time=0, end_time=5)
    ref2 = AssetReference.from_asset(subtitle2, start_time=5, end_time=10)

    # Create scene with subtitle references
    scene = Scene(asset_references=[ref1, ref2])

    # Create project
    project = VideoProject().add_assets([subtitle1, subtitle2]).add_timeline_events(scene)

    # New subtitle params
    new_params = {"font_size": 32, "font_color": "#000000"}

    # Update subtitle params
    project = project.with_subtitle_params(new_params)

    # Check if params were updated for both subtitle assets in scene
    for asset_ref in project.timeline[0].asset_references:
        assert asset_ref.asset_params.font_size == 32
        assert asset_ref.asset_params.font_color.as_hex() == "#000"


def test_with_subtitle_params_mixed() -> None:
    # Create subtitle assets
    subtitle1 = SubtitleAsset.from_data("test 1", id="subtitle1")
    subtitle2 = SubtitleAsset.from_data("test 2", id="subtitle2")
    subtitle3 = SubtitleAsset.from_data("test 3", id="subtitle3")

    # Non-subtitle asset
    text_asset = TextAsset.from_data("text", id="text1")

    # Create asset references
    ref1 = AssetReference.from_asset(subtitle1, start_time=0, end_time=5)
    ref2 = AssetReference.from_asset(subtitle2, start_time=5, end_time=10)
    ref3 = AssetReference.from_asset(subtitle3, start_time=10, end_time=15)
    text_ref = AssetReference.from_asset(text_asset, start_time=0, end_time=5)

    # Create scene with mixed references
    scene = Scene(asset_references=[ref1, ref2, text_ref])

    # Create project with both scene and direct asset reference
    project = (
        VideoProject().add_assets([subtitle1, subtitle2, subtitle3, text_asset]).add_timeline_events([scene, ref3])
    )

    # New subtitle params
    new_params = {"font_size": 40, "font_color": "#FF0000"}

    # Update subtitle params
    project = project.with_subtitle_params(new_params)

    # Check scene subtitles
    for asset_ref in project.timeline[0].asset_references:
        if asset_ref.asset_type == "subtitle":
            assert asset_ref.asset_params.font_size == 40
            assert asset_ref.asset_params.font_color.as_hex().upper() == "#F00"

    # Check direct subtitle reference
    assert project.timeline[1].asset_params.font_size == 40
    assert project.timeline[1].asset_params.font_color.as_hex().upper() == "#F00"

    # Text asset params should be unaffected
    text_ref_scene = [ref for ref in project.timeline[0].asset_references if ref.asset_id == "text1"][0]
    assert text_ref_scene.asset_params == text_asset.params


def test_add_subtitles_from_transcription() -> None:
    transcription = Transcription(
        words=[
            TranscriptionWord(text="Hello", start_time=0.0, end_time=0.5),
            TranscriptionWord(text="world", start_time=0.5, end_time=1.0),
            TranscriptionWord(text="This", start_time=1.0, end_time=1.5),
            TranscriptionWord(text="is", start_time=1.5, end_time=1.7),
            TranscriptionWord(text="a", start_time=1.7, end_time=1.8),
            TranscriptionWord(text="test", start_time=1.8, end_time=2.3),
        ]
    )

    project = VideoProject().add_captions(transcription)

    assert len(project.assets) == 1
    assert len(project.timeline) == 1

    subtitle_asset = next(iter(project.assets.values()))
    assert isinstance(subtitle_asset, SubtitleAsset)
    assert subtitle_asset.data == "Hello world This is a test"

    subtitle_ref = project.timeline[0]
    assert subtitle_ref.start_time == 0.0
    assert subtitle_ref.end_time == 2.3


def test_add_subtitles_from_transcription_with_params() -> None:
    transcription = Transcription(
        words=[
            TranscriptionWord(text="Hello", start_time=0.0, end_time=0.5),
            TranscriptionWord(text="world", start_time=0.5, end_time=1.0),
            TranscriptionWord(text="This", start_time=1.0, end_time=1.5),
            TranscriptionWord(text="is", start_time=1.5, end_time=1.7),
            TranscriptionWord(text="a", start_time=1.7, end_time=1.8),
            TranscriptionWord(text="test", start_time=1.8, end_time=2.3),
        ]
    )

    params = TextAssetParams(font_size=24, font_color="#FFFFFF")
    project = VideoProject().add_captions(transcription, params=params)

    assert len(project.assets) == 1
    assert len(project.timeline) == 1

    subtitle_asset = next(iter(project.assets.values()))
    assert isinstance(subtitle_asset, SubtitleAsset)
    assert subtitle_asset.data == "Hello world This is a test"

    subtitle_ref = project.timeline[0]
    assert subtitle_ref.start_time == 0.0
    assert subtitle_ref.end_time == 2.3
    assert subtitle_ref.asset_params.font_size == 24
    assert subtitle_ref.asset_params.font_color.as_hex().upper() == "#FFF"


def test_add_subtitles_from_transcription_with_max_duration() -> None:
    transcription = Transcription(
        words=[
            TranscriptionWord(text="Hello", start_time=0.0, end_time=0.5),
            TranscriptionWord(text="world", start_time=0.5, end_time=1.0),
            TranscriptionWord(text="This", start_time=1.0, end_time=1.5),
            TranscriptionWord(text="is", start_time=1.5, end_time=1.7),
            TranscriptionWord(text="a", start_time=1.7, end_time=1.8),
            TranscriptionWord(text="test", start_time=1.8, end_time=2.3),
        ]
    )

    project = VideoProject().add_captions(transcription, max_duration=1)

    assert len(project.assets) == 3
    assert len(project.timeline) == 3

    def _get_asset_id(index: int) -> str:
        return list(project.assets.keys())[index]

    subtitle_asset_1 = project.assets[_get_asset_id(0)]
    assert isinstance(subtitle_asset_1, SubtitleAsset)
    assert subtitle_asset_1.data == "Hello world"

    subtitle_ref_1 = project.timeline[0]
    assert subtitle_ref_1.start_time == 0.0
    assert subtitle_ref_1.end_time == 1.0

    subtitle_asset_2 = project.assets[_get_asset_id(1)]
    assert isinstance(subtitle_asset_2, SubtitleAsset)
    assert subtitle_asset_2.data == "This is a"

    subtitle_ref_2 = project.timeline[1]
    assert subtitle_ref_2.start_time == 1.0
    assert subtitle_ref_2.end_time == 1.8

    subtitle_asset_3 = project.assets[_get_asset_id(2)]
    assert isinstance(subtitle_asset_3, SubtitleAsset)
    assert subtitle_asset_3.data == "test"

    subtitle_ref_3 = project.timeline[2]
    assert subtitle_ref_3.start_time == 1.8
    assert subtitle_ref_3.end_time == 2.3


def test_add_narration_resizes_scene_assets():
    # Create initial assets
    subtitle_asset = SubtitleAsset.from_data("test text", id="text1")
    initial_audio = AudioAsset.from_data(
        "initial audio", id="audio1", duration=2.0, sample_rate=44100, sample_width=2, channels=1
    )

    # Create initial scene with text and audio
    text_ref = AssetReference.from_asset(subtitle_asset, start_time=0, end_time=2.0)
    audio_ref = AssetReference.from_asset(initial_audio, start_time=0, end_time=2.0)
    scene = Scene(asset_references=[text_ref, audio_ref])

    # Create project with scene
    project = VideoProject().add_assets([subtitle_asset, initial_audio]).add_timeline_events(scene)

    # Add narration using MockSpeechSynthesizer
    project = project.add_narration(MockSpeechSynthesizer())

    # Get updated scene
    updated_scene = next(event for event in project.timeline if isinstance(event, Scene))

    # Verify all asset references in scene were resized to match narration duration
    # MockSpeechSynthesizer creates audio with duration = len(text) * 0.1
    expected_duration = len(subtitle_asset.to_string()) * 0.1
    for ref in updated_scene.asset_references:
        assert ref.end_time == expected_duration, f"Asset {ref.asset_id} was not resized to match narration duration"


def test_add_narration_to_multiple_scenes():
    # Create assets with different text lengths
    subtitle1 = SubtitleAsset.from_data("short text", id="text1")
    subtitle2 = SubtitleAsset.from_data("this is a longer text", id="text2")

    # Create two scenes
    scene1 = Scene(asset_references=[AssetReference.from_asset(subtitle1, start_time=0, end_time=2.0)])
    scene2 = Scene(asset_references=[AssetReference.from_asset(subtitle2, start_time=0, end_time=3.0)])

    # Create project with both scenes
    project = VideoProject().add_assets([subtitle1, subtitle2]).add_timeline_events([scene1, scene2])

    # Add narration using MockSpeechSynthesizer
    project = project.add_narration(MockSpeechSynthesizer())

    # Verify each scene was resized correctly
    scenes = [event for event in project.timeline if isinstance(event, Scene)]
    assert len(scenes) == 2

    # First scene should match first narration duration
    expected_duration1 = len(subtitle1.to_string()) * 0.1
    for ref in scenes[0].asset_references:
        assert ref.end_time == expected_duration1

    # Second scene should match second narration duration
    expected_duration2 = len(subtitle2.to_string()) * 0.1 + 1
    for ref in scenes[1].asset_references:
        assert ref.end_time == expected_duration2


def test_add_narration_preserves_relative_timing():
    # Create asset that starts mid-scene
    subtitle_asset = SubtitleAsset.from_data("test text", id="text1")

    # Create scene with offset timing
    text_ref = AssetReference.from_asset(subtitle_asset, start_time=1.0, end_time=2.0)  # 1 second offset
    scene = Scene(asset_references=[text_ref])

    # Create project
    project = VideoProject().add_assets(subtitle_asset).add_timeline_events(scene)

    # Add narration using MockSpeechSynthesizer
    project = project.add_narration(MockSpeechSynthesizer())

    # Get updated scene
    updated_scene = next(event for event in project.timeline if isinstance(event, Scene))

    # Calculate expected timings based on MockSpeechSynthesizer's behavior
    narration_duration = len(subtitle_asset.to_string()) * 0.1
    expected_start = 1  # Start time should be 1 second into the scene
    expected_end = narration_duration + 1  # End time should match narration duration + 1 second

    # Verify relative timing
    text_ref = next(ref for ref in updated_scene.asset_references if ref.asset_id == "text1")
    assert text_ref.start_time == expected_start
    assert text_ref.end_time == expected_end
