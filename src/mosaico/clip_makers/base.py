from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from moviepy.Clip import Clip
from pydantic import BaseModel
from pydantic.config import ConfigDict
from pydantic.fields import Field
from pydantic.types import NonNegativeFloat

from mosaico.assets.base import BaseAsset
from mosaico.effects.protocol import Effect
from mosaico.types import FrameSize


T = TypeVar("T", bound=BaseAsset)


class BaseClipMaker(BaseModel, Generic[T], ABC):
    """Base class for clip makers."""

    duration: NonNegativeFloat | None = None
    """The duration of the clip in seconds."""

    video_resolution: FrameSize | None = None
    """The resolution of the video."""

    effects: list[Effect] = Field(default_factory=list)
    """List of effects to apply to the clip."""

    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)

    @abstractmethod
    def _make_clip(self, asset: T) -> Clip:
        """Make a clip from the given clip, duration and video resolution."""
        ...

    def make_clip(self, asset: T) -> Clip:
        """
        Make a clip from the given clip, duration and video resolution.

        :clip: The clip to make the clip from.
        :duration: The duration of the clip in seconds.
        :video_resolution: The resolution of the video.
        :return: The clip.
        """
        clip = self._make_clip(asset)

        for effect in self.effects:
            clip = effect.apply(clip)

        return clip

    def __call__(self, asset: T) -> Clip:
        """
        Make a clip from the given clip, duration and video resolution.

        :clip: The clip to make the clip from.
        :duration: The duration of the clip in seconds.
        :video_resolution: The resolution of the video.
        :return: The clip.
        """
        return self.make_clip(asset)
