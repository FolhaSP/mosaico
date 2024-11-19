from pydantic import BaseModel, PositiveInt
from pydantic.fields import Field
from pydantic.types import NonNegativeFloat, PositiveFloat

from mosaico.effects.types import VideoEffectType


class Shot(BaseModel):
    """A shot for a script."""

    number: PositiveInt
    """The number of the shot."""

    description: str
    """The description of the shot."""

    start_time: NonNegativeFloat
    """The start time of the shot in seconds."""

    end_time: PositiveFloat
    """The end time of the shot in seconds."""

    subtitle: str
    """The subtitle for the shot."""

    media_id: str
    """The media reference for the shot."""

    effects: list[VideoEffectType] = Field(default_factory=list)
    """The effects applied to the shot."""

    @property
    def duration(self) -> float:
        """The duration of the shot in seconds."""
        return self.end_time - self.start_time


class ShootingScript(BaseModel):
    """A shooting script for a video project."""

    title: str
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
