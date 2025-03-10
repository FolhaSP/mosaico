from mosaico.assets.clip import AssetClip, AssetReference
from mosaico.track import Track


def test_timings() -> None:
    clips = [
        AssetClip(asset_reference=AssetReference(id="asset1", type="text"), start_time=0, end_time=10),
        AssetClip(asset_reference=AssetReference(id="asset2", type="text"), start_time=10, end_time=20),
    ]
    track = Track(clips=clips)
    assert track.start_time == 0
    assert track.end_time == 20
    assert track.duration == 20


def test_from_dict() -> None:
    track_dict = {
        "clips": [
            {"asset_reference": {"id": "asset1", "type": "text"}, "start_time": 0, "end_time": 10},
            {"asset_reference": {"id": "asset2", "type": "text"}, "start_time": 10, "end_time": 20},
        ]
    }
    track = Track.from_dict(track_dict)
    assert track.start_time == 0
    assert track.end_time == 20
    assert track.duration == 20


def test_add_clips() -> None:
    clips = [
        AssetClip(asset_reference=AssetReference(id="asset1", type="text"), start_time=0, end_time=10),
        AssetClip(asset_reference=AssetReference(id="asset2", type="text"), start_time=10, end_time=20),
    ]
    track = Track(clips=clips)
    new_clips = [
        AssetClip(asset_reference=AssetReference(id="asset3", type="text"), start_time=20, end_time=30),
        AssetClip(asset_reference=AssetReference(id="asset4", type="text"), start_time=30, end_time=40),
    ]
    track.add_clips(new_clips)
    assert len(track.clips) == 4
    assert track.start_time == 0
    assert track.end_time == 40
    assert track.duration == 40


def test_has_audio() -> None:
    track = Track(
        clips=[
            AssetClip(asset_reference=AssetReference(id="asset1", type="audio"), start_time=0, end_time=10),
            AssetClip(asset_reference=AssetReference(id="asset2", type="text"), start_time=10, end_time=20),
        ]
    )
    assert track.has_audio


def test_has_no_audio() -> None:
    track = Track(
        clips=[
            AssetClip(asset_reference=AssetReference(id="asset1", type="text"), start_time=0, end_time=10),
            AssetClip(asset_reference=AssetReference(id="asset2", type="text"), start_time=10, end_time=20),
        ]
    )
    assert not track.has_audio


def test_has_subtitles() -> None:
    track = Track(
        clips=[
            AssetClip(asset_reference=AssetReference(id="asset1", type="subtitle"), start_time=0, end_time=10),
            AssetClip(asset_reference=AssetReference(id="asset2", type="text"), start_time=10, end_time=20),
        ]
    )
    assert track.has_subtitles


def test_has_no_subtitles() -> None:
    track = Track(
        clips=[
            AssetClip(asset_reference=AssetReference(id="asset1", type="text"), start_time=0, end_time=10),
            AssetClip(asset_reference=AssetReference(id="asset2", type="text"), start_time=10, end_time=20),
        ]
    )
    assert not track.has_subtitles


def test_get_clips_by_type() -> None:
    track = Track(
        clips=[
            AssetClip(asset_reference=AssetReference(id="asset1", type="audio"), start_time=0, end_time=10),
            AssetClip(asset_reference=AssetReference(id="asset2", type="subtitle"), start_time=10, end_time=20),
            AssetClip(asset_reference=AssetReference(id="asset3", type="text"), start_time=20, end_time=30),
            AssetClip(asset_reference=AssetReference(id="asset4", type="text"), start_time=30, end_time=40),
        ]
    )
    assert track.get_clips_by_type("audio") == [
        AssetClip(asset_reference=AssetReference(id="asset1", type="audio"), start_time=0, end_time=10)
    ]
    assert track.get_clips_by_type("subtitle") == [
        AssetClip(asset_reference=AssetReference(id="asset2", type="subtitle"), start_time=10, end_time=20)
    ]
    assert track.get_clips_by_type("text") == [
        AssetClip(asset_reference=AssetReference(id="asset3", type="text"), start_time=20, end_time=30),
        AssetClip(asset_reference=AssetReference(id="asset4", type="text"), start_time=30, end_time=40),
    ]
    assert track.get_clips_by_type("video") == []
    assert track.get_clips_by_type("subtitle", negate=True) == [
        AssetClip(asset_reference=AssetReference(id="asset1", type="audio"), start_time=0, end_time=10),
        AssetClip(asset_reference=AssetReference(id="asset3", type="text"), start_time=20, end_time=30),
        AssetClip(asset_reference=AssetReference(id="asset4", type="text"), start_time=30, end_time=40),
    ]
    assert track.get_clips_by_type(["audio", "subtitle"], negate=True) == [
        AssetClip(asset_reference=AssetReference(id="asset3", type="text"), start_time=20, end_time=30),
        AssetClip(asset_reference=AssetReference(id="asset4", type="text"), start_time=30, end_time=40),
    ]


def test_with_title() -> None:
    track = Track(title="Test track")

    assert track.with_title("New title").title == "New title"


def test_with_description() -> None:
    track = Track(title="Test track")

    assert track.with_description("New description").description == "New description"


def test_with_subtitle_params() -> None:
    clips = [
        AssetClip(asset_reference=AssetReference(id="asset2", type="subtitle"), start_time=10, end_time=20),
    ]
    track = Track().add_clips(clips).with_subtitle_params({"font_size": 100})

    assert track.clips[0].asset_reference.params.font_size == 100
