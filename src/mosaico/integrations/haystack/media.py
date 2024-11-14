from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from mosaico.media import Media


if TYPE_CHECKING:
    from haystack.dataclasses.byte_stream import ByteStream
    from haystack.dataclasses.document import Document


class HaystackDocumentMediaAdapter:
    """
    An adapter for Haystack documents.

    This adapter handles conversion between Mosaico Media objects and Haystack Documents.
    """

    @staticmethod
    def to_external(media: Media) -> Document:
        """
        Convert Media to Haystack Document.

        :param media: The Mosaico media object to convert
        :return: A Haystack Document
        """
        try:
            from haystack.dataclasses.document import Document
        except ImportError:
            raise ImportError("Haystack is not installed")

        metadata = media.metadata.copy()
        metadata.update(
            {
                "path": str(media.path) if media.path else None,
                "mime_type": media.mime_type,
                "media_id": media.id,
                "encoding": media.encoding,
            }
        )

        # Convert binary data using ByteStream adapter if needed
        blob = None
        if media.data is not None or media.path is not None:
            with contextlib.suppress(ValueError, NotImplementedError):
                blob = HaystackByteStreamMediaAdapter.to_external(media)

        return Document(id=media.id, content=media.to_string(), meta=metadata, score=None, blob=blob)

    @staticmethod
    def from_external(doc: Document) -> Media:
        """
        Convert Haystack Document to Media.

        :param doc: The Haystack document to convert
        :return: A Mosaico Media object
        """
        metadata = doc.meta.copy() if doc.meta else {}

        # If we have a blob, use ByteStream adapter
        if doc.blob is not None:
            return HaystackByteStreamMediaAdapter.from_external(doc.blob)

        # Otherwise use the content
        return Media.from_data(
            data=doc.content or "",
            path=metadata.get("path"),
            mime_type=metadata.get("mime_type"),
            encoding=metadata.get("encoding", "utf-8"),
            metadata=metadata,
        )


class HaystackByteStreamMediaAdapter:
    """
    An adapter for Haystack byte streams.
    """

    @staticmethod
    def to_external(media: Media) -> ByteStream:
        """
        Convert Media to Haystack ByteStream.

        :param media: The Mosaico media object to convert
        :return: A Haystack ByteStream
        """
        try:
            from haystack.dataclasses.byte_stream import ByteStream
        except ImportError:
            raise ImportError("Haystack is not installed")

        metadata = media.metadata.copy()
        metadata.update(
            {
                "path": str(media.path) if media.path else None,
                "mime_type": media.mime_type,
                "media_id": media.id,
                "encoding": media.encoding,
            }
        )

        return ByteStream(data=media.to_bytes(), mime_type=media.mime_type or "application/octet-stream", meta=metadata)

    @staticmethod
    def from_external(stream: ByteStream) -> Media:
        """
        Convert Haystack ByteStream to Media.

        :param stream: The Haystack ByteStream to convert
        :return: A Mosaico Media
        """
        metadata = stream.meta.copy() if stream.meta else {}

        return Media.from_data(
            data=stream.data,
            path=metadata.get("path"),
            mime_type=metadata.get("mime_type"),
            encoding=metadata.get("encoding", "utf-8"),
            metadata=metadata,
        )
