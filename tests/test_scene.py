from mosaico.assets.reference import AssetReference
from mosaico.scene import Scene


def test_start_time() -> None:
    asset_references = [
        AssetReference(asset_id="asset1", asset_type="text", start_time=0, end_time=10),
        AssetReference(asset_id="asset2", asset_type="text", start_time=10, end_time=20),
    ]
    scene = Scene(asset_references=asset_references)
    assert scene.start_time == 0


def test_end_time() -> None:
    asset_references = [
        AssetReference(asset_id="asset1", asset_type="text", start_time=0, end_time=10),
        AssetReference(asset_id="asset2", asset_type="text", start_time=10, end_time=20),
    ]
    scene = Scene(asset_references=asset_references)
    assert scene.end_time == 20


def test_duration() -> None:
    asset_references = [
        AssetReference(asset_id="asset1", asset_type="text", start_time=0, end_time=10),
        AssetReference(asset_id="asset2", asset_type="text", start_time=10, end_time=20),
    ]
    scene = Scene(asset_references=asset_references)
    assert scene.duration == 20
