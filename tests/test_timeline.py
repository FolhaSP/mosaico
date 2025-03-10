import pytest

from mosaico.assets.clip import AssetClip, AssetReference
from mosaico.timeline import Timeline
from mosaico.track import Track


def test_empty_timeline():
    timeline = Timeline()

    assert len(timeline) == 0
    assert timeline.duration == 0


def test_timeline_init_with_tracks():
    track1 = Track()
    track2 = Track()
    timeline = Timeline(tracks=[track1, track2])
    assert timeline.tracks == [track1, track2]
    assert len(timeline) == 2


def test_add_single_track():
    track = Track()
    timeline = Timeline().add_tracks(track)

    assert len(timeline) == 1


def test_add_multiple_tracks():
    tracks = [Track(title="Track1"), Track(title="Track2"), Track(title="Track3")]
    timeline = Timeline().add_tracks(tracks)

    assert len(timeline) == 3


def test_duration_calculation():
    track1 = Track()
    clip1 = AssetClip(asset_reference=AssetReference(id="1", type="image"), start_time=0.0, end_time=5.0)
    clip2 = AssetClip(asset_reference=AssetReference(id="2", type="image"), start_time=2.0, end_time=10.0)
    track1.add_clips([clip1, clip2])

    track2 = Track()
    clip3 = AssetClip(asset_reference=AssetReference(id="3", type="audio"), start_time=1.0, end_time=8.0)
    track2.add_clips(clip3)

    timeline = Timeline(tracks=[track1, track2])
    assert timeline.duration == 10.0  # Max end_time is 10.0


def test_duration_empty_timeline():
    timeline = Timeline()
    assert timeline.duration == 0


def test_add_clips_to_track():
    """Test adding clips to a specific track."""
    # Create timeline with tracks
    track0 = Track()
    track1 = Track()
    timeline = Timeline(tracks=[track0, track1])

    # Create clip
    clip = AssetClip(asset_reference=AssetReference(id="1", type="image"), start_time=0.0, end_time=5.0)

    # Add clip to track 1
    result = timeline.add_clips_to_track(clip, 1)

    # Check if the clip was added to the correct track
    assert clip in timeline.tracks[1].clips
    assert len(timeline.tracks[0].clips) == 0  # First track should still be empty
    assert result is timeline  # Method should return self for chaining


def test_add_clips_to_track_multiple():
    """Test adding multiple clips to a specific track."""
    track0 = Track()
    track1 = Track()
    timeline = Timeline(tracks=[track0, track1])

    clips = [
        AssetClip(asset_reference=AssetReference(id="1", type="image"), start_time=0.0, end_time=5.0),
        AssetClip(asset_reference=AssetReference(id="2", type="audio"), start_time=1.0, end_time=6.0),
    ]

    result = timeline.add_clips_to_track(clips, 0)

    # Check if clips were added to the correct track
    assert all(c in timeline.tracks[0].clips for c in clips)
    assert len(timeline.tracks[1].clips) == 0
    assert result is timeline  # Method should return self for chaining


def test_add_clips_to_track_invalid_index():
    """Test adding clips to an invalid track index raises IndexError."""
    timeline = Timeline(tracks=[Track()])
    clip = AssetClip(asset_reference=AssetReference(id="1", type="image"), start_time=0.0, end_time=5.0)

    with pytest.raises(IndexError):
        timeline.add_clips_to_track(clip, 1)  # Track index out of bounds

    with pytest.raises(IndexError):
        timeline.add_clips_to_track(clip, -2)  # Track index out of bounds


def test_timeline_iterator():
    track1 = Track()
    track2 = Track()
    timeline = Timeline(tracks=[track1, track2])

    tracks = list(timeline)
    assert tracks == [track1, track2]


def test_timeline_getitem():
    track1 = Track()
    track2 = Track()
    timeline = Timeline(tracks=[track1, track2])

    assert timeline[0] == track1
    assert timeline[1] == track2

    with pytest.raises(IndexError):
        _ = timeline[2]  # Out of bounds


def test_timeline_setitem():
    track1 = Track()
    track2 = Track()
    timeline = Timeline(tracks=[track1, track2])

    new_track = Track()
    timeline[1] = new_track

    assert timeline.tracks == [track1, new_track]


def test_timeline_delitem():
    track1 = Track()
    track2 = Track()
    timeline = Timeline(tracks=[track1, track2])

    del timeline[0]
    assert timeline.tracks == [track2]
    assert len(timeline) == 1
