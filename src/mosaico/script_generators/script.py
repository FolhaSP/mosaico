from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, PositiveInt
from pydantic.fields import Field
from pydantic.types import NonNegativeFloat

from mosaico.effects.types import EffectType


class ShotMediaReference(BaseModel):
    """A reference to a media object."""

    media_id: str
    """The ID of the media object."""

    type: Literal["image", "video"]
    """The type of the media object."""

    start_time: NonNegativeFloat
    """The start time of the media object in seconds."""

    duration: NonNegativeFloat
    """The duration of the media object in seconds."""

    effects: list[EffectType] = Field(default_factory=list)
    """The effects applied to the media object."""

    @property
    def end_time(self) -> float:
        """The end time of the media object in seconds."""
        return self.start_time + self.duration


class Shot(BaseModel):
    """A shot for a script."""

    number: PositiveInt
    """The number of the shot."""

    description: str
    """The description of the shot."""

    subtitle: str
    """The subtitle for the shot."""

    media_references: list[ShotMediaReference] = Field(default_factory=list)
    """The media references for the shot."""

    @property
    def start_time(self) -> float:
        """The start time of the shot in seconds."""
        if not self.media_references:
            return 0
        return min(media_reference.start_time for media_reference in self.media_references)

    @property
    def end_time(self) -> float:
        """The end time of the shot in seconds."""
        if not self.media_references:
            return 0
        return max(media_reference.end_time for media_reference in self.media_references)

    @property
    def duration(self) -> float:
        """The duration of the shot in seconds."""
        return self.end_time - self.start_time


class ShootingScript(BaseModel):
    """A shooting script for a video project."""

    title: str = "Untitled"
    """The title of the script."""

    description: str | None = None
    """The description of the script."""

    shots: list[Shot] = Field(default_factory=list)
    """The shots in the script."""

    @property
    def duration(self) -> float:
        """The total duration of the script in seconds."""
        return sum(shot.duration or 0 for shot in self.shots)

    @property
    def shot_count(self) -> int:
        """The number of shots in the script."""
        return len(self.shots)
