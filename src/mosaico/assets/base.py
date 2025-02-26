from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Generic, TypeVar, cast

from pydantic import BaseModel
from typing_extensions import Self

from mosaico.media import Media


_ParamsType = TypeVar("_ParamsType", bound=BaseModel)
_InfoType = TypeVar("_InfoType", bound=BaseModel | None)


class BaseAsset(Media, Generic[_ParamsType, _InfoType]):
    """Represents an assets with various properties."""

    type: str
    """The type of the assets."""

    params: _ParamsType
    """The parameters for the assets."""

    info: _InfoType | None = None
    """Information associated with the asset type."""

    @classmethod
    def from_media(cls, media: Media) -> Self:
        """
        Creates an assets from a media object.

        :param media: The media object.
        :return: The assets.
        """
        return cls(**media.model_dump())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        """
        Creates an assets from a dictionary.

        :param data: The dictionary data.
        :return: The assets.
        """
        return cls.model_validate(data)

    @classmethod
    def validate_params(cls, params: Any) -> _ParamsType:
        """
        Validates the parameters for the assets.

        :param params: The parameters to validate.
        :return: The validated parameters.
        """
        params_cls = cls.model_fields["params"].annotation
        params_cls = cast(type[_ParamsType], params_cls)
        return params_cls.model_validate(params)

    def with_params(self, params: _ParamsType | dict[str, Any]) -> Self:
        """
        Returns a new assets with the specified parameters.

        :param params: The parameters to update.
        :return: A new assets with the specified parameters.
        """
        if isinstance(params, BaseModel):
            params = params.model_dump(exclude_unset=True)

        existing_params = self.params.model_dump(exclude_unset=True)
        existing_params.update(params)

        self.params = self.validate_params(existing_params)

        return self

    def _load_info(self) -> None:
        """
        Overwrite this method to set asset lazy-loading logic.
        """
        raise NotImplementedError

    def _safe_get_info_key(self, key: str) -> Any:
        self._load_info()
        if self.info is None:
            raise ValueError("Asset information data could not be loaded.")
        return getattr(self.info, key)
