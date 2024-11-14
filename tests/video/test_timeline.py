import pytest

from mosaico.assets.reference import AssetReference
from mosaico.scene import Scene
from mosaico.video.timeline import Timeline


def test_empty_timeline():
    timeline = Timeline()
    assert len(timeline) == 0
    assert timeline.duration == 0


def test_add_single_asset():
    asset_ref = AssetReference(asset_type="text", asset_id="test", start_time=0, end_time=10)
    timeline = Timeline().add_events(asset_ref)

    assert len(timeline) == 1
    assert timeline.duration == 10
    assert isinstance(timeline[0], AssetReference)


def test_add_single_scene():
    timeline = Timeline()
    scene = Scene(
        title="Test Scene",
        asset_references=[
            AssetReference(asset_id="text1", asset_type="text", path="/path/to/text.txt", start_time=0, end_time=5)
        ],
    )

    timeline.add_events(scene)
    assert len(timeline) == 1
    assert timeline.duration == 5
    assert isinstance(timeline[0], Scene)


def test_add_multiple_events():
    timeline = Timeline()
    events = [
        AssetReference(asset_id="text1", asset_type="text", path="/path/to/text1.txt", start_time=0, end_time=10),
        AssetReference(asset_id="text2", asset_type="text", path="/path/to/text2.txt", start_time=10, end_time=20),
        Scene(
            title="Test Scene",
            asset_references=[
                AssetReference(
                    asset_id="text3", asset_type="text", path="/path/to/text3.txt", start_time=20, end_time=25
                )
            ],
        ),
    ]

    timeline.add_events(events)
    assert len(timeline) == 3
    assert timeline.duration == 25


def test_add_event_from_dict():
    timeline = Timeline()
    asset_dict = {
        "asset_id": "text1",
        "asset_type": "text",
        "path": "/path/to/text.txt",
        "start_time": 0,
        "end_time": 10,
    }

    scene_dict = {
        "title": "Test Scene",
        "asset_references": [
            {"asset_id": "text2", "asset_type": "text", "path": "/path/to/text2.txt", "start_time": 10, "end_time": 15}
        ],
    }

    timeline.add_events([asset_dict, scene_dict])

    assert len(timeline) == 2
    assert isinstance(timeline[0], AssetReference)
    assert isinstance(timeline[1], Scene)


def test_iter_scenes():
    timeline = Timeline()
    events = [
        AssetReference(asset_id="text1", asset_type="text", path="/path/to/text1.txt", start_time=0, end_time=10),
        Scene(
            title="Scene 1",
            asset_references=[
                AssetReference(
                    asset_id="text2", asset_type="text", path="/path/to/text2.txt", start_time=10, end_time=15
                )
            ],
        ),
        Scene(
            title="Scene 2",
            asset_references=[
                AssetReference(
                    asset_id="text3", asset_type="text", path="/path/to/text3.txt", start_time=15, end_time=20
                )
            ],
        ),
    ]

    timeline.add_events(events)
    scenes = list(timeline.iter_scenes())
    assert len(scenes) == 2
    assert all(isinstance(scene, Scene) for scene in scenes)


def test_sort_timeline():
    timeline = Timeline()
    events = [
        Scene(
            title="Scene 2",
            asset_references=[
                AssetReference(
                    asset_id="text1", asset_type="text", path="/path/to/text3.txt", start_time=15, end_time=20
                )
            ],
        ),
        AssetReference(asset_id="text2", asset_type="text", path="/path/to/text2.txt", start_time=0, end_time=10),
        Scene(
            title="Scene 1",
            asset_references=[
                AssetReference(
                    asset_id="text3", asset_type="text", path="/path/to/text3.txt", start_time=10, end_time=15
                )
            ],
        ),
    ]

    timeline.add_events(events)
    timeline.sort()

    assert timeline[0].start_time == 0
    assert timeline[1].start_time == 10
    assert timeline[2].start_time == 15


def test_timeline_indexing():
    timeline = Timeline()
    asset = AssetReference(asset_id="text1", asset_type="text", path="/path/to/text1.txt", start_time=0, end_time=10)

    timeline.add_events(asset)
    timeline[0] = asset
    assert timeline[0] == asset

    del timeline[0]
    assert len(timeline) == 0


def test_invalid_event():
    timeline = Timeline()
    with pytest.raises(ValueError, match="Invalid event type:"):
        timeline.add_events(42)  # type: ignore


def test_timeline_iteration():
    timeline = Timeline()
    events = [
        AssetReference(asset_id="text1", asset_type="text", path="/path/to/text1.txt", start_time=0, end_time=10),
        Scene(start_time=10, end_time=15, elements=[]),
    ]

    timeline.add_events(events)
    assert list(timeline) == events


def test_empty_timeline_duration():
    timeline = Timeline()
    assert timeline.duration == 0


def test_overlapping_events_duration():
    timeline = Timeline()
    events = [
        AssetReference(asset_id="text1", asset_type="text", path="/path/to/text1.txt", start_time=0, end_time=15),
        Scene(
            title="Overlapping Scene",
            asset_references=[
                AssetReference(
                    asset_id="text2", asset_type="text", path="/path/to/text2.txt", start_time=10, end_time=20
                )
            ],
        ),
    ]

    timeline.add_events(events)
    assert timeline.duration == 20


def test_scene_with_multiple_assets():
    timeline = Timeline()
    scene = Scene(
        title="Multi-asset Scene",
        asset_references=[
            AssetReference(asset_id="text1", asset_type="text", path="/path/to/text1.txt", start_time=0, end_time=10),
            AssetReference(asset_id="text2", asset_type="text", path="/path/to/text2.txt", start_time=2, end_time=8),
            AssetReference(asset_id="text3", asset_type="text", path="/path/to/text3.txt", start_time=0, end_time=10),
        ],
    )

    timeline.add_events(scene)
    assert len(timeline) == 1
    assert timeline.duration == 10
    assert len(timeline[0].asset_references) == 3
