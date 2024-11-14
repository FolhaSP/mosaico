from __future__ import annotations

from collections.abc import Mapping, Sequence
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
    """Represents an asset used in a scene."""

    asset_id: str
    """The ID of the asset."""

    asset_type: AssetType
    """The refered asset type."""

    asset_params: AssetParams | None = None
    """The asset reference params."""

    start_time: NonNegativeFloat = 0
    """The start time of the asset in seconds."""

    end_time: NonNegativeFloat = 0
    """The end time of the asset in seconds."""

    effects: list[VideoEffect] = Field(default_factory=list)
    """The effects to apply to the asset."""

    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)

    @model_validator(mode="after")
    def _check_asset_params_type(self) -> AssetReference:
        """
        Check the asset params type.
        """
        asset_params_cls = get_asset_params_class(self.asset_type)
        if self.asset_params is not None and not isinstance(self.asset_params, asset_params_cls):
            msg = f"Asset params must be of type {asset_params_cls.__name__}."
            raise ValueError(msg)
        return self

    @property
    def duration(self) -> float:
        """The duration of the asset in seconds."""
        return self.end_time - self.start_time

    @classmethod
    def from_asset(
        cls,
        asset: Asset,
        *,
        asset_params: AssetParams | None = None,
        start_time: float | None = None,
        end_time: float | None = None,
        effects: Sequence[VideoEffect] | None = None,
    ) -> AssetReference:
        """
        Create an asset reference from an asset.

        :param asset: The asset to reference.
        :param asset_params: The asset params.
        :param start_time: The start time of the asset in seconds.
        :param end_time: The end time of the asset in seconds.
        :return: The asset reference.
        """
        return cls(
            asset_id=asset.id,
            asset_type=asset.type,
            asset_params=asset_params or asset.params,
            start_time=start_time if start_time is not None else 0,
            end_time=end_time if end_time is not None else 0,
            effects=list(effects) if effects is not None else [],
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> AssetReference:
        """
        Create an asset reference from a dictionary.

        :param data: The dictionary data.
        :return: The asset reference.
        """
        if "asset_type" not in data:
            msg = "Missing 'asset_type' key in asset reference data."
            raise ValueError(msg)

        if "asset_params" in data:
            params_cls = get_asset_params_class(data["asset_type"])
            data["asset_params"] = params_cls.model_validate(data["asset_params"])

        return cls.model_validate(data)

    def with_params(self, params: AssetParams) -> AssetReference:
        """
        Add scene params to the asset reference.

        :param params: The scene params to add.
        :return: The asset reference.
        """
        self.asset_params = params
        return self

    def with_start_time(self, start_time: float) -> AssetReference:
        """
        Add a start time to the asset reference.

        :param start_time: The start time to add.
        :return: The asset reference.
        """
        self.start_time = start_time
        return self

    def with_end_time(self, end_time: float) -> AssetReference:
        """
        Add an end time to the asset reference.

        :param end_time: The end time to add.
        :return: The asset reference.
        """
        self.end_time = end_time
        return self

    def with_effects(self, effects: Sequence[Effect]) -> AssetReference:
        """
        Add effects to the asset reference.

        :param effects: The effects to add.
        :return: The asset reference.
        """
        effects = cast(list[VideoEffect], effects)
        self.effects.extend(effects)
        return self
