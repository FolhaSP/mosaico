from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any, Literal, Protocol, TypeVar, runtime_checkable

from pydantic.fields import Field


LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
"""A type alias for log levels."""

FilePath = str | Path
"""A type alias for paths."""

FrameSize = tuple[int, int]
"""A type alias for video resolutions."""

ModelTemperature = Annotated[float, Field(ge=0, le=1)]
"""A type alias for model temperatures."""


# Buffer protocols stolen from pandas, with some minor modifications:
# https://github.com/pandas-dev/pandas/blob/a4e814954b6f1c41528c071b028df62def7765c0/pandas/_typing.py#L266C1-L304C1

# filenames and file-like-objects
AnyStr_co = TypeVar("AnyStr_co", str, bytes, covariant=True)
AnyStr_contra = TypeVar("AnyStr_contra", str, bytes, contravariant=True)


class BaseBuffer(Protocol):
    @property
    def mode(self) -> str:
        # for _get_filepath_or_buffer
        ...

    def seek(self, offset: int, whence: int = ..., /) -> int:
        # with one argument: gzip.GzipFile, bz2.BZ2File
        # with two arguments: zip.ZipFile, read_sas
        ...

    def seekable(self) -> bool:
        # for bz2.BZ2File
        ...

    def tell(self) -> int:
        # for zip.ZipFile, read_stata, to_stata
        ...


@runtime_checkable
class ReadableBuffer(BaseBuffer, Protocol[AnyStr_co]):
    def read(self, n: int = ..., /) -> AnyStr_co:
        # for BytesIOWrapper, gzip.GzipFile, bz2.BZ2File
        ...


@runtime_checkable
class WritableBuffer(BaseBuffer, Protocol[AnyStr_contra]):
    def write(self, b: AnyStr_contra, /) -> Any:
        # for gzip.GzipFile, bz2.BZ2File
        ...

    def flush(self) -> Any:
        # for gzip.GzipFile, bz2.BZ2File
        ...
