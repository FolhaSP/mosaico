from mosaico.assets import create_asset
from mosaico.assets.reference import AssetReference
from mosaico.scene import Scene
from mosaico.video.project import VideoProject, VideoProjectConfig


# Create assets
image = create_asset("image", path="background.jpg")
text = create_asset("text", data="Hello World")

# Create asset references with timing
image_ref = AssetReference.from_asset(image).with_start_time(0).with_end_time(5)
text_ref = AssetReference.from_asset(text).with_start_time(1).with_end_time(4)

# Create scene
scene_1 = Scene(asset_references=[image_ref, text_ref])
scene_2 = Scene(asset_references=[image_ref, text_ref])
scene_3 = Scene(asset_references=[image_ref, text_ref])
scene_4 = Scene(asset_references=[image_ref, text_ref])

# Handle with frame rate
config = VideoProjectConfig(resolution=(1920, 1080), fps=30)

# Create projects
project = (
    VideoProject(config=config)
    .add_assets([image, text])
    .add_timeline_events([scene_3, scene_2, scene_1, scene_4])  # Handle Scene Ordering
)
