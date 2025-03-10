import io

import pytest
import yaml

from mosaico.assets.clip import AssetClip, AssetReference
from mosaico.assets.subtitle import SubtitleAsset
from mosaico.assets.text import TextAsset, TextAssetParams
from mosaico.audio_transcribers.transcription import Transcription, TranscriptionWord
from mosaico.exceptions import AssetNotFoundError, TrackNotFoundError
from mosaico.project import Project, ProjectConfig
from mosaico.track import Track


def test_default_config() -> None:
    config = ProjectConfig()
    assert config.title == "Untitled Project"
    assert config.version == 1
    assert config.rendering_options.resolution == (1920, 1080)
    assert config.rendering_options.fps == 30


def test_add_single_asset() -> None:
    asset = TextAsset.from_data("test", id="asset_1")
    project = Project().add_assets(asset)
    assert "asset_1" in project.asset_map
    assert project.asset_map["asset_1"].id == asset.id
    assert project.asset_map["asset_1"].data == "test"


def test_add_single_dict_asset() -> None:
    asset = {"id": "asset_1", "type": "text", "data": "test"}
    project = Project().add_assets(asset)
    assert "asset_1" in project.asset_map
    assert project.asset_map["asset_1"].id == asset["id"]
    assert project.asset_map["asset_1"].data == "test"


def test_add_multiple_assets() -> None:
    assets = [TextAsset.from_data("test", id="asset_1"), TextAsset.from_data("test", id="asset_2")]
    project = Project().add_assets(assets)
    assert "asset_1" in project.asset_map
    assert project.asset_map["asset_1"].id == assets[0].id
    assert project.asset_map["asset_1"].data == "test"
    assert "asset_2" in project.asset_map
    assert project.asset_map["asset_2"].id == assets[1].id
    assert project.asset_map["asset_2"].data == "test"


def test_add_multiple_dict_assets() -> None:
    assets = [{"id": "asset_1", "type": "text", "data": "test"}, {"id": "asset_2", "type": "text", "data": "test"}]
    project = Project().add_assets(assets)
    assert "asset_1" in project.asset_map
    assert project.asset_map["asset_1"].id == assets[0]["id"]
    assert project.asset_map["asset_1"].data == "test"
    assert "asset_2" in project.asset_map
    assert project.asset_map["asset_2"].id == assets[1]["id"]
    assert project.asset_map["asset_2"].data == "test"


def test_add_single_track_to_timeline() -> None:
    track = Track()
    project = Project().add_tracks(track)
    assert project.timeline.tracks == [track]


def test_add_multiple_tracks_to_timeline() -> None:
    track1 = Track()
    track2 = Track()
    project = Project().add_tracks([track1, track2])
    assert project.timeline.tracks == [track1, track2]


def test_add_single_dict_track_to_timeline() -> None:
    track = {"description": "Track 1"}
    project = Project().add_tracks(track)
    assert project.timeline.tracks[0].model_dump(exclude_unset=True) == track


def test_add_multiple_dict_tracks_to_timeline() -> None:
    track1 = {"description": "Track 1"}
    track2 = {"description": "Track 2"}
    project = Project().add_tracks([track1, track2])
    assert project.timeline.tracks[0].model_dump(exclude_unset=True) == track1
    assert project.timeline.tracks[1].model_dump(exclude_unset=True) == track2


def test_add_track_with_invalid_asset_id() -> None:
    invalid_clip = AssetClip(asset_reference=AssetReference(id="invalid", type="image"))
    track = Track().add_clips(invalid_clip)
    with pytest.raises(AssetNotFoundError, match="Asset with ID 'invalid' not found in the project assets"):
        Project().add_tracks(track)


def test_get_track() -> None:
    track = Track(description="Track 1")
    project = Project().add_tracks(track)
    assert project.timeline.tracks[0] == track


def test_get_out_of_range_track_index_error() -> None:
    track = Track(description="Track 1")
    project = Project().add_tracks(track)
    with pytest.raises(TrackNotFoundError, match="Track index out of range"):
        project.get_track(2)


def test_remove_track() -> None:
    track = Track(description="Track 1")
    project = Project().add_tracks(track)
    project.remove_track(0)
    assert len(project.timeline.tracks) == 0


def test_remove_out_of_range_track_index_error() -> None:
    track = Track(description="Track 1")
    project = Project().add_tracks(track)
    with pytest.raises(TrackNotFoundError, match="Track index out of range"):
        project.remove_track(1)


def test_duration() -> None:
    project = Project()
    assert project.duration == 0

    text_asset = TextAsset.from_data("test", id="test_1")
    tracks = [
        Track(description="Track 1", clips=[AssetClip.from_asset(text_asset, start_time=0, end_time=10)]),
        Track(description="Track 2", clips=[AssetClip.from_asset(text_asset, start_time=0, end_time=20)]),
    ]
    project = project.add_assets(text_asset).add_tracks(tracks)

    assert project.duration == 20


def test_get_asset() -> None:
    asset = TextAsset.from_data("test", id="asset1")
    project = Project().add_assets(asset)
    assert project.get_asset("asset1") == asset
    with pytest.raises(AssetNotFoundError, match="Asset with ID 'nonexistent' not found in the project assets"):
        project.get_asset("nonexistent")


def test_get_asset_out_of_bound() -> None:
    asset = TextAsset.from_data("test", id="asset1")
    project = Project().add_assets(asset)
    with pytest.raises(AssetNotFoundError, match="Asset with ID 'asset2' not found in the project assets"):
        project.get_asset("asset2")


@pytest.fixture
def mock_project_file(tmp_path):
    project_data = {
        "config": {"title": "Test Project", "version": 1, "rendering_options": {"resolution": (1920, 1080), "fps": 30}},
        "asset_map": {"asset1": {"type": "text", "data": "test", "id": "asset1"}},
        "timeline": {
            "tracks": [
                {
                    "title": "Track 1",
                    "clips": [{"asset_reference": {"id": "asset1", "type": "text"}, "start_time": 0, "end_time": 10}],
                }
            ]
        },
    }
    project_file = tmp_path / "project.yaml"
    project_file.write_text(yaml.safe_dump(project_data))
    return project_file


def test_from_file_success(mock_project_file):
    project = Project.from_file(mock_project_file)

    assert project.config.title == "Test Project"
    assert project.config.rendering_options.resolution == (1920, 1080)
    assert project.config.rendering_options.fps == 30
    assert "asset1" in project.asset_map
    assert project.asset_map["asset1"].type == "text"
    assert project.asset_map["asset1"].data == "test"
    assert project.asset_map["asset1"].id == "asset1"
    assert project.timeline.tracks[0].title == "Track 1"
    assert project.timeline.tracks[0].clips[0].asset_reference.id == "asset1"
    assert project.timeline.tracks[0].clips[0].start_time == 0
    assert project.timeline.tracks[0].clips[0].end_time == 10


def test_from_file_string_buffer(mock_project_file):
    project_buf = io.StringIO(mock_project_file.read_text())
    project = Project.from_file(project_buf)
    assert project.config.title == "Test Project"
    assert project.config.rendering_options.resolution == (1920, 1080)
    assert project.config.rendering_options.fps == 30
    assert project.asset_map == {"asset1": TextAsset.from_data("test", id="asset1")}
    assert project.timeline.tracks == [
        Track(
            title="Track 1",
            clips=[AssetClip(asset_reference=AssetReference(id="asset1", type="text"), start_time=0, end_time=10)],
        )
    ]


def test_from_file_invalid_path():
    with pytest.raises(FileNotFoundError):
        Project.from_file("non_existent_file.yaml")


def test_to_file(mock_project_file, tmp_path):
    project = Project.from_file(mock_project_file)
    project_file = tmp_path / "project.yaml"
    project.to_file(project_file)
    assert project_file.read_text() == mock_project_file.read_text()


def test_to_file_string_buffer(mock_project_file) -> None:
    project = Project.from_file(mock_project_file)
    project_file = io.StringIO()
    project.to_file(project_file)
    assert Project.from_file(project_file) == project


# class MockScriptGenerator:
#     def generate(self, media: Sequence[Media], **kwargs: Any) -> ShootingScript:
#         return ShootingScript(
#             title="Test Script",
#             description="This is a test script",
#             shots=[
#                 Shot(
#                     number=1,
#                     description="Shot 1",
#                     start_time=0,
#                     end_time=5,
#                     subtitle="Hello world",
#                     media_id=media[0].id,
#                 ),
#                 Shot(
#                     number=2,
#                     description="Shot 2",
#                     start_time=5,
#                     end_time=10,
#                     subtitle="This is a test",
#                     media_id=media[1].id,
#                 ),
#             ],
#         )


# class MockSpeechSynthesizer:
#     provider: ClassVar[str] = "test"

#     def synthesize(
#         self, texts: Sequence[str], *, audio_params: AudioAssetParams | None = None, **kwargs: Any
#     ) -> list[AudioAsset]:
#         return [
#             AudioAsset.from_data(
#                 "test_audio",
#                 id="test_audio",
#                 mime_type="audio/wav",
#                 info=AudioInfo(
#                     duration=len(text) * 0.1,
#                     sample_width=16,
#                     sample_rate=44100,
#                     channels=1,
#                 ),
#             )
#             for text in texts
#         ]


# class MockAudioTranscriber:
#     def transcribe(self, audio_asset: AudioAsset) -> Transcription:
#         words = audio_asset.to_string().split()  # Assume audio.data is the text
#         return Transcription(
#             words=[
#                 TranscriptionWord(text=word, start_time=i * 0.5, end_time=(i + 1) * 0.5) for i, word in enumerate(words)
#             ]
#         )


# # Subtitle Tests
# @pytest.fixture
# def sample_transcription():
#     return Transcription(
#         words=[
#             TranscriptionWord(text="Hello", start_time=0.0, end_time=0.5),
#             TranscriptionWord(text="world", start_time=0.5, end_time=1.0),
#             TranscriptionWord(text="This", start_time=1.0, end_time=1.5),
#             TranscriptionWord(text="is", start_time=1.5, end_time=2.0),
#             TranscriptionWord(text="a", start_time=2.0, end_time=2.2),
#             TranscriptionWord(text="test", start_time=2.2, end_time=2.5),
#         ]
#     )


# def test_add_captions_basic(sample_transcription):
#     project = VideoProject().add_captions(sample_transcription)

#     # Verify assets were created
#     subtitle_assets = [asset for asset in project.asset_map.values() if isinstance(asset, SubtitleAsset)]
#     assert len(subtitle_assets) == 1

#     # Verify timeline events
#     subtitle_refs = [ref for ref in project.timeline if isinstance(project.asset_map[ref.asset_id], SubtitleAsset)]
#     assert len(subtitle_refs) == 1
#     assert subtitle_refs[0].start_time == 0.0
#     assert subtitle_refs[0].end_time == 2.5


# def test_add_captions_with_max_duration(sample_transcription):
#     project = VideoProject().add_captions(sample_transcription, max_duration=1)

#     # Should split into multiple subtitle assets/references
#     subtitle_refs = [ref for ref in project.timeline if isinstance(project.asset_map[ref.asset_id], SubtitleAsset)]
#     assert len(subtitle_refs) == 3

#     # Verify timing of segments
#     assert subtitle_refs[0].start_time == 0.0
#     assert subtitle_refs[0].end_time == 1.0
#     assert subtitle_refs[1].start_time == 1.0
#     assert subtitle_refs[1].end_time == 2.0
#     assert subtitle_refs[2].start_time == 2.0
#     assert subtitle_refs[2].end_time == 2.5


# def test_add_captions_with_params(sample_transcription):
#     params = TextAssetParams(font_size=24, font_color="#FFFFFF")
#     project = VideoProject().add_captions(sample_transcription, params=params)

#     subtitle_refs = [ref for ref in project.timeline if ref.asset_type == "subtitle"]
#     assert len(subtitle_refs) == 1

#     # Verify params were applied
#     assert subtitle_refs[0].asset_params.font_size == 24
#     assert subtitle_refs[0].asset_params.font_color.as_hex().upper() == "#FFF"


# @patch("mosaico.audio_transcribers.protocol.AudioTranscriber")
# def test_add_captions_from_transcriber(mock_transcriber, sample_transcription):
#     # Setup
#     audio_asset = AudioAsset.from_data(
#         "test_audio", id="audio1", info=AudioInfo(duration=2.5, sample_rate=44100, sample_width=128, channels=1)
#     )
#     mock_transcriber.transcribe.return_value = sample_transcription

#     # Create project with audio in timeline
#     scene = Scene(description="Test scene")
#     ref = AssetReference.from_asset(audio_asset, start_time=0, end_time=2.5)
#     scene = scene.add_asset_references(ref)

#     project = VideoProject().add_assets(audio_asset).add_timeline_events(scene)

#     # Add captions
#     project = project.add_captions_from_transcriber(mock_transcriber)

#     # Verify transcriber was called
#     mock_transcriber.transcribe.assert_called_once_with(audio_asset)

#     # Verify subtitles were added to scene
#     scene = next(event for event in project.timeline if isinstance(event, Scene))
#     subtitle_refs = [ref for ref in scene.asset_references if isinstance(project.assets[ref.asset_id], SubtitleAsset)]
#     assert len(subtitle_refs) > 0


# def test_from_script_generator():
#     media = [
#         Media.from_data("test1", id="1", mime_type="text/plain"),
#         Media.from_data("test2", id="2", mime_type="text/plain"),
#     ]

#     project = VideoProject.from_script_generator(script_generator=MockScriptGenerator(), media=media)

#     assert isinstance(project, VideoProject)
#     assert len(project.timeline) == 2


# def test_group_words_into_phrases():
#     transcription = Transcription(
#         words=[
#             TranscriptionWord(text="Hello", start_time=0.0, end_time=0.5),
#             TranscriptionWord(text="world", start_time=0.5, end_time=1.0),
#             TranscriptionWord(text="This", start_time=1.0, end_time=1.5),
#             TranscriptionWord(text="is", start_time=1.5, end_time=1.7),
#             TranscriptionWord(text="a", start_time=1.7, end_time=1.8),
#             TranscriptionWord(text="test", start_time=1.8, end_time=2.3),
#             TranscriptionWord(text="with", start_time=2.3, end_time=2.6),
#             TranscriptionWord(text="numbers", start_time=2.6, end_time=3.1),
#             TranscriptionWord(text="123.45", start_time=3.1, end_time=3.6),
#         ]
#     )

#     phrases = _group_transcript_into_sentences(transcription, max_duration=2.0)

#     assert len(phrases) == 2
#     assert " ".join(word.text for word in phrases[0]) == "Hello world This is a"
#     assert " ".join(word.text for word in phrases[1]) == "test with numbers 123.45"


# def test_group_words_into_phrases_with_numbers():
#     transcription = Transcription(
#         words=[
#             TranscriptionWord(text="The", start_time=0.0, end_time=0.2),
#             TranscriptionWord(text="number", start_time=0.2, end_time=0.5),
#             TranscriptionWord(text="is", start_time=0.5, end_time=0.7),
#             TranscriptionWord(text="123", start_time=0.7, end_time=1.0),
#             TranscriptionWord(text=".", start_time=1.0, end_time=1.1),
#             TranscriptionWord(text="45", start_time=1.1, end_time=1.4),
#             TranscriptionWord(text="and", start_time=1.4, end_time=1.6),
#             TranscriptionWord(text="6,789", start_time=1.6, end_time=2.0),
#         ]
#     )

#     phrases = _group_transcript_into_sentences(transcription, max_duration=1.5)

#     assert len(phrases) == 2
#     assert " ".join(word.text for word in phrases[0]) == "The number is 123 . 45"
#     assert " ".join(word.text for word in phrases[1]) == "and 6,789"


@pytest.mark.parametrize("config", [ProjectConfig(title="Test"), {"title": "Test"}], ids=["object", "dict"])
def test_with_config(config) -> None:
    project = Project().with_config(config)

    assert project.config.title == "Test"


def test_with_subtitle_params() -> None:
    # Create a subtitle asset
    subtitle_asset = SubtitleAsset.from_data("test text", id="subtitle1")

    # Create project with timeline event
    clip = AssetClip.from_asset(subtitle_asset, start_time=0, end_time=10)
    track = Track().add_clips(clip)
    project = Project().add_assets(subtitle_asset).add_tracks(track)

    # New subtitle params
    new_params = {"font_size": 24, "font_color": "#FFFFFF"}

    # Update subtitle params
    project = project.with_subtitle_params(new_params)

    # Check if params were updated
    assert project.timeline.tracks[0].clips[0].asset_reference.params.font_size == 24  # type: ignore
    assert project.timeline.tracks[0].clips[0].asset_reference.params.font_color.as_hex().upper() == "#FFF"  # type: ignore


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

    project = Project().add_captions(transcription)

    assert len(project.asset_map) == 1
    assert len(project.timeline.tracks) == 1

    subtitle_asset = next(iter(project.asset_map.values()))
    assert isinstance(subtitle_asset, SubtitleAsset)
    assert subtitle_asset.data == "Hello world This is a test"
    print(project.timeline.tracks)

    subtitle_clip = project.timeline.tracks[0].clips[0]
    assert subtitle_clip.start_time == 0.0
    assert subtitle_clip.end_time == 2.3


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

    params = TextAssetParams(font_size=24, font_color="#FFFFFF")  # type: ignore
    project = Project().add_captions(transcription, params=params)

    assert len(project.asset_map) == 1
    assert len(project.timeline.tracks) == 1

    subtitle_asset = next(iter(project.asset_map.values()))
    assert isinstance(subtitle_asset, SubtitleAsset)
    assert subtitle_asset.data == "Hello world This is a test"

    subtitle_clip = project.timeline.tracks[0].clips[0]
    assert subtitle_clip.start_time == 0.0
    assert subtitle_clip.end_time == 2.3
    assert subtitle_clip.asset_reference.params.font_size == 24  # type: ignore
    assert subtitle_clip.asset_reference.params.font_color.as_hex().upper() == "#FFF"  # type: ignore


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

    project = Project().add_captions(transcription, max_duration=1)

    assert len(project.asset_map) == 3
    assert len(project.timeline.tracks) == 1

    def _get_asset_id(index: int) -> str:
        return list(project.asset_map.keys())[index]

    subtitle_asset_1 = project.asset_map[_get_asset_id(0)]
    assert isinstance(subtitle_asset_1, SubtitleAsset)
    assert subtitle_asset_1.data == "Hello world"

    subtitle_clip_1 = project.timeline.tracks[0].clips[0]
    assert subtitle_clip_1.start_time == 0.0
    assert subtitle_clip_1.end_time == 1.0

    subtitle_asset_2 = project.asset_map[_get_asset_id(1)]
    assert isinstance(subtitle_asset_2, SubtitleAsset)
    assert subtitle_asset_2.data == "This is a"

    subtitle_clip_2 = project.timeline.tracks[0].clips[1]
    assert subtitle_clip_2.start_time == 1.0
    assert subtitle_clip_2.end_time == 1.8

    subtitle_asset_3 = project.asset_map[_get_asset_id(2)]
    assert isinstance(subtitle_asset_3, SubtitleAsset)
    assert subtitle_asset_3.data == "test"

    subtitle_clip_3 = project.timeline.tracks[0].clips[2]
    assert subtitle_clip_3.start_time == 1.8
    assert subtitle_clip_3.end_time == 2.3


# def test_add_narration_resizes_scene_assets():
#     # Create initial assets
#     subtitle_asset = SubtitleAsset.from_data("test text", id="text1")
#     initial_audio = AudioAsset.from_data(
#         "initial audio", id="audio1", info=AudioInfo(duration=2.0, sample_rate=44100, sample_width=2, channels=1)
#     )

#     # Create initial scene with text and audio
#     text_ref = AssetReference.from_asset(subtitle_asset, start_time=0, end_time=2.0)
#     audio_ref = AssetReference.from_asset(initial_audio, start_time=0, end_time=2.0)
#     scene = Scene(asset_references=[text_ref, audio_ref])

#     # Create project with scene
#     project = VideoProject().add_assets([subtitle_asset, initial_audio]).add_timeline_events(scene)

#     # Add narration using MockSpeechSynthesizer
#     project = project.add_narration(MockSpeechSynthesizer())

#     # Get updated scene
#     updated_scene = next(event for event in project.timeline if isinstance(event, Scene))

#     # Verify all asset references in scene were resized to match narration duration
#     # MockSpeechSynthesizer creates audio with duration = len(text) * 0.1
#     expected_duration = len(subtitle_asset.to_string()) * 0.1
#     for ref in updated_scene.asset_references:
#         assert ref.end_time == expected_duration, f"Asset {ref.asset_id} was not resized to match narration duration"


# def test_add_narration_to_multiple_scenes():
#     # Create assets with different text lengths
#     subtitle1 = SubtitleAsset.from_data("short text", id="text1")
#     subtitle2 = SubtitleAsset.from_data("this is a longer text", id="text2")

#     # Create two scenes
#     scene1 = Scene(asset_references=[AssetReference.from_asset(subtitle1, start_time=0, end_time=2.0)])
#     scene2 = Scene(asset_references=[AssetReference.from_asset(subtitle2, start_time=0, end_time=3.0)])

#     # Create project with both scenes
#     project = VideoProject().add_assets([subtitle1, subtitle2]).add_timeline_events([scene1, scene2])

#     # Add narration using MockSpeechSynthesizer
#     project = project.add_narration(MockSpeechSynthesizer())

#     # Verify each scene was resized correctly
#     scenes = [event for event in project.timeline if isinstance(event, Scene)]
#     assert len(scenes) == 2

#     # First scene should match first narration duration
#     expected_duration1 = len(subtitle1.to_string()) * 0.1
#     for ref in scenes[0].asset_references:
#         assert ref.end_time == expected_duration1

#     # Second scene should match second narration duration
#     expected_duration2 = len(subtitle2.to_string()) * 0.1 + 1
#     for ref in scenes[1].asset_references:
#         assert ref.end_time == expected_duration2


# def test_add_narration_preserves_relative_timing():
#     # Create asset that starts mid-scene
#     subtitle_asset = SubtitleAsset.from_data("test text", id="text1")

#     # Create scene with offset timing
#     text_ref = AssetReference.from_asset(subtitle_asset, start_time=1.0, end_time=2.0)  # 1 second offset
#     scene = Scene(asset_references=[text_ref])

#     # Create project
#     project = VideoProject().add_assets(subtitle_asset).add_timeline_events(scene)

#     # Add narration using MockSpeechSynthesizer
#     project = project.add_narration(MockSpeechSynthesizer())

#     # Get updated scene
#     updated_scene = next(event for event in project.timeline if isinstance(event, Scene))

#     # Calculate expected timings based on MockSpeechSynthesizer's behavior
#     narration_duration = len(subtitle_asset.to_string()) * 0.1
#     expected_start = 1  # Start time should be 1 second into the scene
#     expected_end = narration_duration + 1  # End time should match narration duration + 1 second

#     # Verify relative timing
#     text_ref = next(ref for ref in updated_scene.asset_references if ref.asset_id == "text1")
#     assert text_ref.start_time == expected_start
#     assert text_ref.end_time == expected_end
