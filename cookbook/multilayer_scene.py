from mosaico.assets import create_asset
from mosaico.assets.image import ImageAssetParams
from mosaico.assets.reference import AssetReference
from mosaico.effects.pan import PanLeftEffect, PanRightEffect
from mosaico.effects.zoom import ZoomInEffect, ZoomOutEffect
from mosaico.positioning import AbsolutePosition, RegionPosition
from mosaico.scene import Scene
from mosaico.video.project import VideoProject, VideoProjectConfig


# Create assets
images = [
    create_asset("image", path="background.jpg"),
    create_asset("image", path="logo.jpg"),
    create_asset("image", path="credits.jpg"),
]

image_refs = [
    AssetReference.from_asset(images[0])
    .with_start_time(0)
    .with_end_time(10)
    .with_effects(effects=[ZoomInEffect(), PanLeftEffect()])
    .with_params(params=ImageAssetParams(z_index=0, as_background=True)),
    AssetReference.from_asset(images[1])
    .with_start_time(0)
    .with_end_time(10)
    .with_effects(effects=[ZoomOutEffect(), PanRightEffect()])
    .with_params(params=ImageAssetParams(crop=(0, 0, 120, 120), position=AbsolutePosition(x=10, y=10), z_index=1)),
    AssetReference.from_asset(images[2])
    .with_start_time(0)
    .with_end_time(10)
    .with_effects(effects=[ZoomOutEffect(), PanRightEffect()])
    .with_params(
        params=ImageAssetParams(crop=(120, 120, 220, 220), position=RegionPosition(x="right", y="bottom"), z_index=1)
    ),
]

# Create scene
scene = Scene(asset_references=image_refs)

# Create project
project = VideoProject(config=VideoProjectConfig()).add_assets(images).add_timeline_events(scene)
