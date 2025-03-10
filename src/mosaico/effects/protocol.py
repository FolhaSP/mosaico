from typing import Any, LiteralString, Protocol, TypeVar, runtime_checkable


T = TypeVar("T", bound=LiteralString)


@runtime_checkable
class Effect(Protocol[T]):
    """
    A protocol for clip effects.

    !!! note
        This is a runtime checkable protocol, which means ``isinstance()`` and
        ``issubclass()`` checks can be performed against it.
    """

    type: T
    """The type of the effect."""

    def get_params(self) -> dict[str, Any]:
        """Return the parameters of the effect."""
        ...
