from mosaico.assets import create_asset
from mosaico.assets.reference import AssetReference
from mosaico.assets.text import TextAssetParams
from mosaico.scene import Scene
from mosaico.video.project import VideoProject, VideoProjectConfig


# Subtitles
subtitles = [
    create_asset(
        "text",
        data="First Scene Subtitles",
        params=TextAssetParams(font_size=20, font_family="Arial", align="center", z_index=1),
    ),
    create_asset(
        "text",
        data="Second Scene Subtitles",
        params=TextAssetParams(font_size=20, font_family="Arial", align="right", z_index=2),
    ),
    create_asset(
        "text",
        data="Second Scene center Subtitles",
        params=TextAssetParams(font_size=20, font_family="Arial", align="center", z_index=2),
    ),
    create_asset(
        "text",
        data="Third Scene Subtitles",
        params=TextAssetParams(font_size=20, font_family="Arial", align="left", z_index=2),
    ),
]

# Create references
subtitles_refs = [
    AssetReference.from_asset(subtitles[0]).with_start_time(0).with_end_time(10),
    AssetReference.from_asset(subtitles[1]).with_start_time(10).with_end_time(20),
    AssetReference.from_asset(subtitles[2]).with_start_time(10).with_end_time(20),
    AssetReference.from_asset(subtitles[3]).with_start_time(20).with_end_time(30),
]

# Create scene
scene_1 = Scene(asset_references=[subtitles_refs[0]])
scene_2 = Scene(asset_references=[subtitles_refs[1], subtitles_refs[2]])
scene_3 = Scene(asset_references=[subtitles_refs[3]])


# Create project
project = (
    VideoProject(config=VideoProjectConfig()).add_assets(subtitles).add_timeline_events([scene_1, scene_2, scene_3])
)
