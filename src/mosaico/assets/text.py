from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, NonNegativeFloat, NonNegativeInt
from pydantic.fields import Field
from pydantic.functional_serializers import field_serializer
from pydantic_extra_types.color import Color

from mosaico.assets.base import BaseAsset
from mosaico.positioning import AbsolutePosition, Position


class TextAssetParams(BaseModel):
    """Represents the parameters for a text assets."""

    position: Position = Field(default_factory=AbsolutePosition)
    """The positioning of the text assets in the video."""

    font_family: str = "Arial Bold"
    """The font family."""

    font_size: NonNegativeInt = 70
    """The font size."""

    font_color: Color = Field(default_factory=lambda: Color("#000000"))
    """The font color hexadecimal code."""

    font_kerning: float = 0
    """The font kerning."""

    line_height: int = 10
    """The line height."""

    stroke_color: Color = Field(default_factory=lambda: Color("#000000"))
    """The font stroke color hexadecimal code."""

    stroke_width: NonNegativeFloat = 0
    """The font stroke width."""

    shadow_color: Color = Field(default_factory=lambda: Color("#000000"))
    """The shadow color hexadecimal code."""

    shadow_blur: int = 0
    """The shadow blur."""

    shadow_opacity: Annotated[float, Field(ge=0, le=1)] = 1
    """The shadow opacity."""

    shadow_angle: int = 0
    """The shadow angle."""

    shadow_distance: NonNegativeInt = 0
    """The shadow distance."""

    background_color: Color = Field(default_factory=lambda: Color("transparent"))
    """The background color hexadecimal code."""

    align: Literal["left", "center", "right"] = "left"
    """The text alignment."""

    z_index: int = 0
    """The z-index of the assets."""

    @field_serializer("font_color", "stroke_color", "shadow_color", "background_color", when_used="always")
    def serialize_color(self, value: Color) -> str:
        """Serialize the color to its hexadecimal code."""
        return value.as_hex()


class BaseTextAsset(BaseAsset[TextAssetParams]):
    """Represents a text assets with various properties."""

    params: TextAssetParams = Field(default_factory=TextAssetParams)
    """The parameters for the text assets."""

    @property
    def has_background(self) -> bool:
        """
        Check if the text asset has a background.
        """
        return self.params.background_color.as_named() != "transparent"

    @property
    def has_shadow(self) -> bool:
        """
        Check if the text asset has a shadow.
        """
        return self.params.shadow_color.as_named() != "transparent" and self.params.shadow_opacity > 0


class TextAsset(BaseTextAsset):
    """Represents a text assets with various properties."""

    type: Literal["text"] = "text"
    """¨The type of the assets. Defaults to "text"."""
