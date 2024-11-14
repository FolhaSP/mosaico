from __future__ import annotations

from typing import Protocol, TypeVar, runtime_checkable

from moviepy.Clip import Clip
from pydantic import BaseModel


T_contra = TypeVar("T_contra", bound=BaseModel, contravariant=True)


@runtime_checkable
class ClipMaker(Protocol[T_contra]):
    """
    A protocol for clip makers.
    """

    def make_clip(self, asset: T_contra) -> Clip:
        """
        Make a clip from the given asset.
        """
        ...
