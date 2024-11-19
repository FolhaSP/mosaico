from __future__ import annotations

from typing import Any, Literal

from pydantic.fields import Field
from pydantic.functional_validators import field_validator
from pydantic_extra_types.color import Color

from mosaico.assets.text import BaseTextAsset, TextAssetParams
from mosaico.positioning import RegionPosition, is_region_position
from mosaico.script_generators.script import Shot


class SubtitleAsset(BaseTextAsset):
    """Represents a subtitles assets."""

    type: Literal["subtitle"] = "subtitle"
    """The type of the assets. Defaults to "subtitle"."""

    params: TextAssetParams = Field(
        default_factory=lambda: TextAssetParams(
            position=RegionPosition(x="center", y="bottom"),
            font_color=Color("white"),
            font_size=45,
            stroke_width=1,
            align="center",
            shadow_blur=10,
            shadow_angle=135,
            shadow_opacity=0.5,
            shadow_distance=5,
        )
    )
    """The parameters for the assets."""

    @field_validator("params", mode="after")
    @classmethod
    def check_position_is_region(cls, params: TextAssetParams) -> TextAssetParams:
        """
        Validate that the subtitle positioning is of type RegionPosition.
        """
        if not is_region_position(params.position):
            raise ValueError("Subtitle positioning must be of type RegionPosition")
        if not params.position.x == "center":
            raise ValueError("Subtitle x position must be 'center'")
        return params

    @classmethod
    def from_shot(cls, shot: Shot, **kwargs: Any) -> SubtitleAsset:
        """
        Create a SubtitleAsset from a Shot.

        :param shot: The shot to create the asset from.
        :param kwargs: Additional parameters for the asset.
        :return: The created asset.
        """
        return cls.from_data(shot.subtitle, **kwargs)
