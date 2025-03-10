from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

from pydantic import BaseModel
from pydantic.config import ConfigDict
from pydantic.fields import Field
from pydantic.functional_validators import model_validator
from pydantic.types import NonNegativeFloat

from mosaico.assets.factory import get_asset_params_class
from mosaico.assets.types import Asset, AssetParams, AssetType
from mosaico.effects.protocol import Effect
from mosaico.effects.types import VideoEffect


class AssetReference(BaseModel):
    """
    Information about the clip referenced asset.
    """

    id: str
    """The ID of the asset."""

    type: AssetType
    """The refered asset type."""

    params: AssetParams | None = None
    """The asset reference params."""


class AssetClip(BaseModel):
    """
    Represents an asset used in a track.
    """

    asset_reference: AssetReference
    """The reference of the clip asset."""

    start_time: NonNegativeFloat = 0
    """The start time of the asset in seconds."""

    duration: NonNegativeFloat | None = None
    """The duration of the asset in seconds."""

    effects: list[VideoEffect] = Field(default_factory=list)
    """The effects to apply to the asset."""

    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)

    @model_validator(mode="after")
    def _check_asset_params_type(self) -> AssetClip:
        """
        Check the asset params type.
        """
        asset_ref = self.asset_reference
        asset_params_cls = get_asset_params_class(asset_ref.type)
        if asset_ref.params is not None and not isinstance(asset_ref.params, asset_params_cls):
            msg = f"Asset params must be of type {asset_params_cls.__name__}."
            raise ValueError(msg)
        return self

    @property
    def end_time(self) -> float:
        """The end time of the asset in seconds."""
        return self.start_time + (self.duration or 0)

    @classmethod
    def from_asset(
        cls,
        asset: Asset,
        *,
        params: AssetParams | None = None,
        start_time: float | None = None,
        duration: float | None = None,
        effects: Sequence[VideoEffect] | None = None,
    ) -> AssetClip:
        """
        Create a clip from an asset.

        :param asset: The asset to reference.
        :param params: The asset params.
        :param start_time: The start time of the asset in seconds.
        :param end_time: The end time of the asset in seconds.
        :return: The asset reference.
        """
        asset_ref = AssetReference(id=asset.id, type=asset.type, params=params or asset.params)
        return cls(
            asset_reference=asset_ref,
            effects=list(effects) if effects is not None else [],
            start_time=start_time if start_time is not None else 0,
            duration=duration,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AssetClip:
        """
        Create an asset reference from a dictionary.

        :param data: The dictionary data.
        :return: The asset reference.
        """
        if "asset_reference" not in data:
            msg = "Missing 'asset_reference' key in asset clip data."
            raise ValueError(msg)

        if "params" in data["asset_reference"] and data["asset_reference"]["params"] is not None:
            params_cls = get_asset_params_class(data["asset_reference"]["type"])
            data["asset_reference"]["params"] = params_cls.model_validate(data["asset_reference"]["params"])

        return cls.model_validate(data)

    def with_params(self, params: AssetParams) -> AssetClip:
        """
        Add scene params to the asset reference.

        :param params: The scene params to add.
        :return: The asset reference.
        """
        self.asset_reference.params = params
        return self

    def with_start_time(self, start_time: float) -> AssetClip:
        """
        Add a start time to the asset reference.

        :param start_time: The start time to add.
        :return: The asset reference.
        """
        self.start_time = start_time
        return self

    def with_duration(self, duration: float) -> AssetClip:
        """
        Add a duration to the asset reference.

        :param duration: The duration to add.
        :return: The asset reference.
        """
        self.duration = duration
        return self

    def with_effects(self, effects: Sequence[Effect]) -> AssetClip:
        """
        Add effects to the asset reference.

        :param effects: The effects to add.
        :return: The asset reference.
        """
        effects = cast(list[VideoEffect], effects)
        self.effects.extend(effects)
        return self
