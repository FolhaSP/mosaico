from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel
from pydantic.config import ConfigDict
from pydantic.fields import Field

from mosaico.assets.reference import AssetReference
from mosaico.assets.text import TextAssetParams


class Scene(BaseModel):
    """Represents a unit of grouped asset references in a timeline."""

    title: str | None = None
    """An optional title of the scene."""

    description: str | None = None
    """An optional description of the scene."""

    asset_references: list[AssetReference] = Field(default_factory=list)
    """A list of assets associated with the scene."""

    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Scene:
        """
        Create a scene from a dictionary.

        :param data: The dictionary data.
        :return: The scene.
        """
        asset_refs = []

        for asset_ref in data.get("asset_references", []):
            if isinstance(asset_ref, Mapping):
                asset_ref = AssetReference.from_dict(asset_ref)
            asset_refs.append(asset_ref)

        return cls(
            title=data.get("title"),
            description=data.get("description"),
            asset_references=asset_refs,
        )

    @property
    def start_time(self) -> float:
        """
        The start time of the scene in seconds.
        """
        if not self.asset_references:
            return 0
        return min(ref.start_time for ref in self.asset_references)

    @property
    def end_time(self) -> float:
        """
        The end time of the scene in seconds.
        """
        if not self.asset_references:
            return 0
        return max(ref.end_time for ref in self.asset_references)

    @property
    def duration(self) -> float:
        """
        The duration of the scene in seconds.
        """
        return self.end_time - self.start_time

    @property
    def has_audio(self) -> bool:
        """
        Check if the scene has an audio asset.
        """
        return any(ref.asset_type == "audio" for ref in self.asset_references)

    @property
    def has_subtitles(self) -> bool:
        """
        Check if the scene has a subtitle asset.
        """
        return any(ref.asset_type == "subtitle" for ref in self.asset_references)

    def add_asset_references(self, references: AssetReference | Sequence[AssetReference]) -> Scene:
        """
        Add asset references to the scene.

        :param references: The asset references to add.
        :return: The scene.
        """
        references = references if isinstance(references, Sequence) else [references]
        self.asset_references.extend(references)
        return self

    def remove_asset_id_references(self, asset_id: str) -> Scene:
        """
        Remove asset references by asset ID.

        :param asset_id: The asset ID to remove.
        :return: The scene.
        """
        self.asset_references = [ref for ref in self.asset_references if ref.asset_id != asset_id]
        return self

    def with_subtitle_params(self, params: TextAssetParams | Mapping[str, Any]) -> Scene:
        """
        Add subtitle asset params to the scene.

        :param params: The subtitle asset params.
        :return: The scene.
        """
        for ref in self.asset_references:
            if ref.asset_type == "subtitle":
                ref.asset_params = TextAssetParams.model_validate(params)
        return self
