from __future__ import annotations

import uuid
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel
from pydantic.config import ConfigDict
from pydantic.fields import Field

from mosaico.assets.clip import AssetClip
from mosaico.assets.text import TextAssetParams
from mosaico.assets.types import AssetType


class Track(BaseModel):
    """Represents a unit of grouped asset references in a timeline."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    """The unique identifier of the track."""

    title: str | None = None
    """An optional title of the scene."""

    description: str | None = None
    """An optional description of the scene."""

    clips: list[AssetClip] = Field(default_factory=list)
    """A list of assets associated with the scene."""

    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Track:
        """
        Create a scene from a dictionary.

        :param data: The dictionary data.
        :return: The scene.
        """
        clips = []

        for clip in data.get("clips", []):
            clip = AssetClip.from_dict(clip)
            clips.append(clip)

        return cls(
            title=data.get("title"),
            description=data.get("description"),
            clips=clips,
        )

    @property
    def start_time(self) -> float:
        """
        The start time of the scene in seconds.
        """
        return min(ref.start_time for ref in self.clips) if self.clips else 0

    @property
    def end_time(self) -> float:
        """
        The end time of the scene in seconds.
        """
        return max(ref.end_time for ref in self.clips) if self.clips else 0

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
        return any(self.get_clips_by_type("audio"))

    @property
    def has_subtitles(self) -> bool:
        """
        Check if the scene has a subtitle asset.
        """
        return any(self.get_clips_by_type("subtitle"))

    @property
    def has_video(self) -> bool:
        """
        Check if the scene has a video asset.
        """
        return any(self.get_clips_by_type("video"))

    @property
    def has_image(self) -> bool:
        """
        Check if the scene has an image asset.
        """
        return any(self.get_clips_by_type("image"))

    def add_clips(self, clip_or_clips: AssetClip | Sequence[AssetClip]) -> Track:
        """
        Add clips to the track.

        :param clip_or_clips: A single clip or an array of them.
        :return: The track with the added clips.
        """
        new_clips = clip_or_clips if isinstance(clip_or_clips, Sequence) else [clip_or_clips]
        self.clips.extend(new_clips)
        return self

    def get_clips_by_type(
        self, type_or_types: AssetType | Sequence[AssetType], *, negate: bool = False
    ) -> list[AssetClip]:
        """
        Get all track clips by asset type.

        :param type_or_types: A single asset type of an array of them.
        :param negate: Whether to filter the oposite of the provided type(s).
        :return: The track clips that match the criteria.
        """
        types = type_or_types if isinstance(type_or_types, Sequence) else [type_or_types]
        return [clip for clip in self.clips if (clip.asset_reference.type in types) is not negate]

    def remove_clips_by_asset_id(self, asset_id: str) -> Track:
        """
        Remove asset references by asset ID.

        :param asset_id: The asset ID to remove.
        :return: The track.
        """
        self.clips = [clip for clip in self.clips if clip.asset_reference.id != asset_id]
        return self

    def with_title(self, title: str) -> Track:
        """
        Set the track title.

        :param title: The track title.
        :return: The track.
        """
        self.title = title
        return self

    def with_description(self, description: str) -> Track:
        """
        Set the track description.

        :param description: The track description.
        :return: The track.
        """
        self.description = description
        return self

    def with_subtitle_params(self, params: TextAssetParams | Mapping[str, Any]) -> Track:
        """
        Add subtitle asset params to the track subtitles.

        :param params: The subtitle asset params.
        :return: The track.
        """
        for clip in self.clips:
            if clip.asset_reference.type == "subtitle":
                clip.asset_reference.params = TextAssetParams.model_validate(params)
        return self
