from typing import Protocol, TypeVar, runtime_checkable

from mosaico.effects.protocol import Effect


T = TypeVar("T")
E_contra = TypeVar("E_contra", bound=Effect, contravariant=True)


@runtime_checkable
class EffectAdapter(Protocol[T, E_contra]):
    """
    Abstract base class for engine-specific effect adapters.

    Effect adapters are responsible for taking engine-agnostic effects and
    applying them to engine-specific clip objects.
    """

    def apply(self, obj: T, effect: E_contra) -> T:
        """
        Apply an effect to an engine-specific object.

        :param clip: An engine-specific clip object
        :param effect: An engine-agnostic effect definition
        :return: The modified clip
        """
        ...
