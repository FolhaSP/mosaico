from __future__ import annotations

import base64
import binascii
import contextlib
import io
import mimetypes
import re
import uuid
from collections.abc import Generator
from typing import IO, Any, cast

import fsspec
from pydantic import BaseModel
from pydantic.config import ConfigDict
from pydantic.fields import Field
from pydantic.functional_serializers import field_serializer
from pydantic.functional_validators import field_validator, model_validator
from typing_extensions import Self

from mosaico.config import settings
from mosaico.integrations.base.adapters import Adapter
from mosaico.types import FilePath


_BASE64_BYTE_PATTERN = re.compile(rb"^[A-Za-z0-9+/]+={0,2}$")


class Media(BaseModel):
    """
    Represents a media object.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    """The unique identifier of the assets."""

    data: str | bytes | None = None
    """The content of the media."""

    path: FilePath | None = None
    """The path to the media."""

    mime_type: str | None = None
    """The MIME type of the media."""

    encoding: str = "utf-8"
    """The encoding of the media."""

    metadata: dict[str, Any] = Field(default_factory=dict)
    """The metadata of the media."""

    storage_options: dict[str, Any] = Field(default_factory=settings.storage_options.copy)
    """Media's storage options."""

    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True, extra="forbid")

    @property
    def description(self) -> str:
        """
        Returns a description of the media.
        """
        return self.metadata.get("description", "")

    @property
    def credits(self) -> str:
        """
        Returns the credits of the media.
        """
        return self.metadata.get("credits", "")

    @model_validator(mode="before")
    @classmethod
    def validate_media(cls, values: dict[str, Any]) -> Any:
        """
        Validates the content of the media.
        """
        if "data" not in values and "path" not in values:
            raise ValueError("Either data or path must be provided")

        return values

    @field_validator("data")
    @classmethod
    def decode_base64_data(cls, v: bytes | str | None) -> bytes | str | None:
        """
        Decode field data from Base64 only if it looks like Base64.
        """
        if isinstance(v, str):
            try:
                raw = v.encode("ascii")
            except UnicodeEncodeError:
                return v

            if len(raw) % 4 == 0 and _BASE64_BYTE_PATTERN.match(raw) is not None and raw.endswith(b"="):
                try:
                    return base64.b64decode(raw, validate=True)
                except binascii.Error:
                    pass
        return v

    @field_serializer("data", when_used="json")
    def encode_base64_data(self, v) -> str:
        """
        Codifica campo data em base64.
        """
        if isinstance(v, bytes):
            return base64.b64encode(v).decode(self.encoding)
        return v

    @classmethod
    def from_path(
        cls,
        path: FilePath,
        *,
        encoding: str = "utf-8",
        mime_type: str | None = None,
        guess_mime_type: bool = True,
        metadata: dict | None = None,
        **kwargs: Any,
    ) -> Self:
        """
        Creates a media from a path.

        :param path: The path to the media.
        :param encoding: The encoding of the media.
        :param mime_type: The MIME type of the media.
        :param guess_mime_type: Whether to guess the MIME type.
        :param metadata: The metadata of the media.
        :param kwargs: Additional keyword arguments to the constructor.
        :return: The media.
        """
        if not mime_type and guess_mime_type:
            mime_type = mimetypes.guess_type(str(path))[0]

        return cls(
            data=None,
            path=path,
            metadata=metadata if metadata is not None else {},
            encoding=encoding,
            mime_type=mime_type,
            **kwargs,
        )

    @classmethod
    def from_data(
        cls,
        data: str | bytes,
        *,
        path: FilePath | None = None,
        metadata: dict | None = None,
        mime_type: str | None = None,
        **kwargs: Any,
    ) -> Self:
        """
        Creates a media from data.

        :param data: The data of the media.
        :param path: The path to the media.
        :param metadata: The metadata of the media.
        :param mime_type: The MIME type of the media.
        :param kwargs: Additional keyword arguments to the constructor.
        :return: The media.
        """
        return cls(
            data=data,
            path=path,
            metadata=metadata if metadata is not None else {},
            mime_type=mime_type,
            **{k: v for k, v in kwargs.items() if v is not None},
        )

    @classmethod
    def from_external(cls, adapter: Adapter[Media, Any], external: Any) -> Media:
        """
        Converts an external representation to a media.
        """
        return adapter.from_external(external)

    def to_external(self, adapter: Adapter[Media, Any]) -> Any:
        """
        Converts the media to an external representation.
        """
        return adapter.to_external(self)

    def to_string(self, **kwargs: Any) -> str:
        """
        Returns the media as a string.
        """
        if isinstance(self.data, str):
            return self.data
        if isinstance(self.data, bytes):
            return self.data.decode(self.encoding)
        if self.data is None and self.path is not None:
            kwargs["mode"] = "r"
            with self.open(**kwargs) as f:
                return cast(str, f.read())
        raise ValueError("Data is not a string or bytes")

    def to_bytes(self, **kwargs: Any) -> bytes:
        """
        Returns the media as bytes.
        """
        if isinstance(self.data, bytes):
            return self.data
        if isinstance(self.data, str):
            return self.data.encode(self.encoding)
        if self.data is None and self.path is not None:
            kwargs["mode"] = "rb"
            with self.open(**kwargs) as f:
                return cast(bytes, f.read())
        raise ValueError("Data is not a string or bytes")

    @contextlib.contextmanager
    def to_bytes_io(self, **kwargs: Any) -> Generator[IO[bytes], None, None]:
        """
        Read data as a byte stream.
        """
        if isinstance(self.data, bytes):
            yield io.BytesIO(self.data)
        elif self.data is None and self.path:
            kwargs["mode"] = "rb"
            with self.open(**kwargs) as f:
                yield cast(IO[bytes], f)
        else:
            raise NotImplementedError(f"Unable to convert blob {self}")

    @contextlib.contextmanager
    def open(self, **kwargs) -> Generator[IO[bytes] | IO[str], None, None]:
        """
        Opens the media for read/write operations.
        """
        if self.path is None:
            raise ValueError("File-opening could only be done when 'path' is not missing.")
        fs, path_str = fsspec.core.url_to_fs(self.path, **self.storage_options)
        with fs.open(path_str, **kwargs) as f:
            yield f

    def add_metadata(self, metadata: dict[str, Any]) -> Self:
        """
        Add metadata to the media object.
        """
        self.metadata.update(metadata)
        return self

    def with_metadata(self, metadata: dict[str, Any]) -> Self:
        """
        Set media object metadata.
        """
        self.metadata = metadata
        return self

    def with_storage_options(self, storage_options: dict[str, Any]) -> Self:
        """
        Add/replace storage options of the media object.
        """
        self.storage_options = storage_options
        return self
