from __future__ import annotations

from typing import Any, Protocol, TypeVar, runtime_checkable


Adapted = TypeVar("Adapted", bound=Any)
Adaptable = TypeVar("Adaptable", bound=Any)


@runtime_checkable
class Adapter(Protocol[Adapted, Adaptable]):
    """
    A protocol for adapters.
    """

    def to_external(self, obj: Adapted) -> Adaptable:
        """Converts the object to an external representation."""
        ...

    def from_external(self, external: Adaptable) -> Adapted:
        """Converts the external representation to an object."""
        ...
