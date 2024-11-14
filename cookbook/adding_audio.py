from mosaico.assets import create_asset
from mosaico.assets.audio import AudioAssetParams
from mosaico.assets.reference import AssetReference
from mosaico.scene import Scene
from mosaico.video.project import VideoProject, VideoProjectConfig


# Create assets
images = [...]
image_refs = [...]


audios = [
    create_asset("audio", path="human_music.mp3"),
    create_asset("audio", path="human_music_2.mp3"),
    create_asset("audio", path="human_music_3.mp3"),
    create_asset("audio", path="human_music_4.mp3"),
]

# Mixing Audio using the same Time Span
music_1 = (
    AssetReference.from_asset(audios[0])
    .with_start_time(0)
    .with_end_time(10)
    .with_params(params=AudioAssetParams(volume=0.5))
)
music_2 = (
    AssetReference.from_asset(audios[1])
    .with_start_time(0)
    .with_end_time(10)
    .with_params(params=AudioAssetParams(volume=0.5))
)

music_3 = (
    AssetReference.from_asset(audios[2])
    .with_start_time(10)
    .with_end_time(15)
    .with_params(params=AudioAssetParams(volume=1))
)
music_4 = (
    AssetReference.from_asset(audios[3])
    .with_start_time(10)
    .with_end_time(20)
    .with_params(params=AudioAssetParams(volume=0.5))
)

# Create scene
scene = Scene(asset_references=image_refs + [music_1, music_2, music_3, music_4])

# Create project
project = VideoProject(config=VideoProjectConfig()).add_assets(images).add_assets(audios).add_timeline_events(scene)
