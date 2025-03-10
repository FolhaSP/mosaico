from __future__ import annotations

from collections.abc import Iterator, Sequence

from pydantic import BaseModel, Field

from mosaico.assets.clip import AssetClip
from mosaico.track import Track


class Timeline(BaseModel):
    """
    A representation of a timeline.
    """

    tracks: list[Track] = Field(default_factory=list)

    @property
    def duration(self) -> float:
        """
        The total duration of the timeline in seconds.
        """
        return max(event.end_time for event in self.tracks) if self.tracks else 0

    def add_tracks(self, tracks: Track | Sequence[Track]) -> Timeline:
        """
        Add tracks to the timeline.

        :param tracks: The tracks to add.
        :return: The timeline with the tracks added.
        """
        new_tracks = tracks if isinstance(tracks, Sequence) else [tracks]
        self.tracks.extend(new_tracks)
        return self

    def add_clips_to_track(self, clips: AssetClip | Sequence[AssetClip], track_index: int) -> Timeline:
        """
        Add clips to a track in the timeline.

        :param clips: The clips to add.
        :param track_index: The index of the track to add the clips to.
        :return: The timeline with the clips added.
        """
        if track_index < 0 or track_index > len(self.tracks):
            raise IndexError(f"Track index is out of bounds: {track_index}")
        self.tracks[track_index].add_clips(clips)
        return self

    def __len__(self) -> int:
        """
        The number of tracks in the timeline.
        """
        return len(self.tracks)

    def __iter__(self) -> Iterator[Track]:  # type: ignore
        """
        Iterate over the tracks in the timeline.
        """
        return iter(self.tracks)

    def __getitem__(self, index: int) -> Track:
        """
        Get a track by index.

        :param index: The index of the track to get.
        :return: The track at the given index.
        """
        return self.tracks[index]

    def __setitem__(self, index: int, track: Track) -> None:
        """
        Set a track at a given index.

        :param index: The index of the track to set.
        :param track: The track to set.
        """
        self.tracks[index] = track

    def __delitem__(self, index: int) -> None:
        """
        Delete a track at a given index.

        :param index: The index of the track to delete.
        """
        del self.tracks[index]
