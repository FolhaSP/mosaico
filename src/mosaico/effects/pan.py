from typing import Literal

from pydantic.types import PositiveFloat

from mosaico.effects.base import BaseEffect


class BasePanEffect(BaseEffect):
    """A pan effect."""

    zoom_factor: PositiveFloat = 1.1
    """The zoom factor."""


class PanLeftEffect(BasePanEffect):
    """A pan left effect."""

    type: Literal["pan_left"] = "pan_left"


class PanRightEffect(BasePanEffect):
    """A pan right effect."""

    type: Literal["pan_right"] = "pan_right"


class PanUpEffect(BasePanEffect):
    """A pan up effect."""

    type: Literal["pan_up"] = "pan_up"


class PanDownEffect(BasePanEffect):
    """A pan down effect."""

    type: Literal["pan_down"] = "pan_down"


class PanCenterEffect(BasePanEffect):
    """A pan center effect."""

    type: Literal["pan_center"] = "pan_center"
