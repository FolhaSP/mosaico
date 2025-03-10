from unittest.mock import MagicMock

import numpy as np
import pytest
from pydantic_extra_types.color import Color

from mosaico.assets.audio import AudioAsset, AudioAssetParams
from mosaico.assets.clip import AssetClip, AssetReference
from mosaico.assets.image import ImageAsset, ImageAssetParams
from mosaico.assets.text import TextAsset, TextAssetParams
from mosaico.positioning.absolute import AbsolutePosition
from mosaico.project import Project, ProjectConfig
from mosaico.rendering.types import RenderingOptions
from mosaico.track import Track


@pytest.fixture
def rendering_options():
    options = RenderingOptions()
    options.resolution = (1280, 720)
    options.fps = 30
    return options


@pytest.fixture
def audio_asset():
    asset = MagicMock(spec=AudioAsset)
    asset.params = AudioAssetParams()
    asset.type = "audio"
    asset.duration = 5.0
    asset.params.volume = 1.0
    asset.params.crop = None
    asset.sample_width = 2
    asset.sample_rate = 44100
    asset.channels = 2
    asset.to_bytes_io.return_value.__enter__.return_value = MagicMock()
    return asset


@pytest.fixture
def image_asset():
    asset = MagicMock(spec=ImageAsset)
    asset.params = ImageAssetParams()
    asset.type = "image"
    asset.size = (1280, 720)
    asset.params.as_background = False
    asset.params.position = AbsolutePosition()
    asset.to_bytes.return_value = np.zeros((720, 1280, 3), dtype=np.uint8).tobytes()
    return asset


@pytest.fixture
def text_asset():
    asset = MagicMock(spec=TextAsset)
    asset.params = TextAssetParams()
    asset.type = "text"
    asset.has_shadow = False
    asset.params.font_family = "Arial"
    asset.params.font_size = 32
    asset.params.line_height = 1.2
    asset.params.align = "center"
    asset.params.font_color = MagicMock(Color)
    asset.params.font_color.as_rgb_tuple.return_value = (255, 255, 255, 1.0)
    asset.params.stroke_color = MagicMock(Color)
    asset.params.stroke_color.as_hex.return_value = "#000000"
    asset.params.stroke_width = 0
    asset.params.position = AbsolutePosition()
    asset.to_string.return_value = "Test Text"
    return asset


@pytest.fixture
def audio_clip(audio_asset):
    ref = AssetReference(id="audio1", type="audio", params=audio_asset.params)
    clip = AssetClip(asset_reference=ref)
    clip.start_time = 0.0
    clip.end_time = 5.0
    return clip


@pytest.fixture
def image_clip(image_asset):
    ref = AssetReference(id="image1", type="image", params=image_asset.params)
    clip = AssetClip(asset_reference=ref)
    clip.start_time = 0.0
    clip.end_time = 5.0
    return clip


@pytest.fixture
def text_clip(text_asset):
    ref = AssetReference(id="text1", type="text", params=text_asset.params)
    clip = AssetClip(asset_reference=ref)
    clip.start_time = 0.0
    clip.end_time = 5.0
    return clip


@pytest.fixture
def asset_map(audio_asset, image_asset, text_asset):
    return {
        "audio1": audio_asset,
        "image1": image_asset,
        "text1": text_asset,
    }


@pytest.fixture
def track(audio_clip, image_clip, text_clip):
    track = Track()
    track.clips = [audio_clip, image_clip, text_clip]
    return track


@pytest.fixture
def empty_track():
    return Track()


@pytest.fixture
def project(track, asset_map):
    config = ProjectConfig()
    config.title = "Test Project"
    config.rendering_options = RenderingOptions()
    config.rendering_options.resolution = (1280, 720)
    config.rendering_options.fps = 30

    project = Project()
    project.config = config
    project.timeline.tracks = [track]
    project.asset_map = asset_map

    return project
