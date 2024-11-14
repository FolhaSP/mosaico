from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from typing import Any, TypeAlias, TypeVar

from pydantic.fields import Field
from pydantic.root_model import RootModel

from mosaico.assets.reference import AssetReference
from mosaico.scene import Scene
from mosaico.video.types import TimelineEvent


T = TypeVar("T")
Event: TypeAlias = T | Mapping[str, Any]
EventSequence: TypeAlias = Sequence[Event[T]]
EventOrEventSequence: TypeAlias = Event[AssetReference | Scene] | EventSequence[AssetReference | Scene]


class Timeline(RootModel):
    """
    Represents and manages a sequence of timeline events.
    """

    root: list[TimelineEvent] = Field(default_factory=list)
    """A list of timeline events."""

    @property
    def duration(self) -> float:
        """
        The total duration of the timeline in seconds.
        """
        if not self.root:
            return 0
        return max([event.end_time for event in self.root])

    def add_events(self, event: EventOrEventSequence) -> Timeline:
        """
        Add one or more events to the timeline.

        :param event: The event or events to add.
        :return: The timeline.
        """
        if isinstance(event, (AssetReference, Scene)):
            self.root.append(event)
            return self

        if isinstance(event, Mapping):
            if "asset_type" in event:
                return self._add_asset_reference(event)
            return self._add_scene(event)

        if isinstance(event, Sequence):
            for item in event:
                self.add_events(item)
            return self

        msg = f"Invalid event type: {type(event)}"
        raise ValueError(msg)

    def iter_scenes(self) -> Iterator[Scene]:
        """
        Iterate over scenes in the timeline.
        """
        for event in self.root:
            if isinstance(event, Scene):
                yield event

    def sort(self) -> Timeline:
        """
        Sort the timeline events.
        """
        self.root.sort(key=lambda x: x.start_time)
        return self

    def _add_asset_reference(self, reference: Event[AssetReference]) -> Timeline:
        """
        Add an asset reference to the timeline.
        """
        if isinstance(reference, Mapping):
            self.root.append(AssetReference.from_dict(reference))
        else:
            self.root.append(reference)
        return self

    def _add_scene(self, scene: Event[Scene]) -> Timeline:
        """
        Add a scene to the timeline.
        """
        if isinstance(scene, Mapping):
            self.root.append(Scene.from_dict(scene))
        else:
            self.root.append(scene)
        return self

    def __iter__(self):  # type: ignore
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    def __setitem__(self, item, value):
        self.root[item] = value

    def __delitem__(self, item):
        del self.root[item]

    def __len__(self):
        return len(self.root)
