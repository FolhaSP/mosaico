from typing import Any

from mosaico.effects.pan import PanDownEffect, PanLeftEffect, PanRightEffect, PanUpEffect
from mosaico.effects.protocol import Effect
from mosaico.effects.zoom import ZoomInEffect, ZoomOutEffect


EFFECT_MAP: dict[str, type[Effect]] = {
    "pan_left": PanLeftEffect,
    "pan_right": PanRightEffect,
    "pan_up": PanUpEffect,
    "pan_down": PanDownEffect,
    "zoom_in": ZoomInEffect,
    "zoom_out": ZoomOutEffect,
}


def create_effect(effect_type: str, **params: Any) -> Effect:
    """
    Create an effect.

    :param effect_type: The type of the effect.
    :param params: The effect parameters.
    :return: The effect.
    """
    effect_cls = EFFECT_MAP.get(effect_type)

    if effect_cls is None:
        raise ValueError(f"Invalid effect type: {effect_type}")

    return effect_cls(**params)