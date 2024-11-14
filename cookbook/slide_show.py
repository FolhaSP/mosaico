from mosaico.assets import create_asset
from mosaico.assets.reference import AssetReference
from mosaico.scene import Scene
from mosaico.video.project import VideoProject, VideoProjectConfig


# Create assets
images = [
    create_asset("image", path="photo_1.jpg"),
    create_asset("image", path="photo_2.jpg"),
    create_asset("image", path="photo_3.jpg"),
    create_asset("image", path="photo_4.jpg"),
    create_asset("image", path="photo_5.jpg"),
    create_asset("image", path="photo_6.jpg"),
]

image_refs = [
    AssetReference.from_asset(image).with_start_time(i * 5).with_end_time((i + 1) * 5) for i, image in enumerate(images)
]


background_music = create_asset("audio", path="human_music.mp3")
audio_ref = AssetReference.from_asset(background_music).with_start_time(0).with_end_time(len(images) * 5)

# Create scene
scene = Scene(asset_references=image_refs)

# Create project
project = (
    VideoProject(config=VideoProjectConfig())
    .add_assets(images)
    .add_assets([background_music])
    .add_timeline_events(scene)
)
