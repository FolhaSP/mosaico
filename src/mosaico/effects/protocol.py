from typing import Protocol, TypeVar, runtime_checkable

from moviepy.Clip import Clip


ClipType = TypeVar("ClipType", bound=Clip)


@runtime_checkable
class Effect(Protocol[ClipType]):
    """
    A protocol for clip effects.

    !!! note
        This is a runtime checkable protocol, which means ``isinstance()`` and
        ``issubclass()`` checks can be performed against it.
    """

    def apply(self, clip: ClipType) -> ClipType:
        """Apply the effect to the clip."""
        ...
