from mosaico.assets import create_asset
from mosaico.assets.reference import AssetReference
from mosaico.effects.pan import PanLeftEffect, PanRightEffect
from mosaico.effects.zoom import ZoomInEffect, ZoomOutEffect
from mosaico.scene import Scene
from mosaico.video.project import VideoProject, VideoProjectConfig


# Create assets
images = [
    create_asset("image", path="photo_1.jpg"),
    create_asset("image", path="photo_2.jpg"),
]

image_refs = [
    AssetReference.from_asset(images[0])
    .with_start_time(0)
    .with_end_time(5)
    .with_effects(effects=[ZoomInEffect(), PanLeftEffect()]),
    AssetReference.from_asset(images[1])
    .with_start_time(5)
    .with_end_time(10)
    .with_effects(effects=[ZoomOutEffect(), PanRightEffect()]),
]

# Create scene
scene = Scene(asset_references=image_refs)

# Create project
project = VideoProject(config=VideoProjectConfig()).add_assets(images).add_timeline_events(scene)
