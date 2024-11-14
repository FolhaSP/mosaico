from __future__ import annotations

from typing import Literal

from mosaico.assets.audio import AudioAsset, AudioAssetParams
from mosaico.assets.image import ImageAsset, ImageAssetParams
from mosaico.assets.subtitle import SubtitleAsset
from mosaico.assets.text import TextAsset, TextAssetParams


AssetType = Literal["video", "image", "audio", "text", "subtitle"]
"""An enumeration of the different types of assets that can be held in an assets."""

Asset = AudioAsset | ImageAsset | TextAsset | SubtitleAsset
"""Represents an assets with various properties."""

AssetParams = AudioAssetParams | ImageAssetParams | TextAssetParams
"""Represents the parameters of an assets."""
