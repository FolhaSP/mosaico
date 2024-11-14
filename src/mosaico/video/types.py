from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, TypeAlias

from mosaico.assets import AssetReference
from mosaico.assets.types import Asset
from mosaico.scene import Scene


TimelineEvent = AssetReference | Scene
"""A type alias for a timeline event, which can be an asset reference or a scene."""

AssetInputType: TypeAlias = Mapping[str, Any] | Asset | Sequence[dict[str, Any]] | Sequence[Asset]
"""A type alias for the input type of an asset."""

TimelineEventInputType: TypeAlias = (
    Mapping[str, Any] | TimelineEvent | Sequence[dict[str, Any]] | Sequence[TimelineEvent]
)
"""A type alias for the input type of a timeline event."""
