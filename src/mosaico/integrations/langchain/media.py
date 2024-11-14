from __future__ import annotations

from typing import TYPE_CHECKING

from mosaico.media import Media


if TYPE_CHECKING:
    from langchain_core.documents.base import Blob, Document


class LangChainDocumentMediaAdapter:
    """
    An adapter for LangChain documents.

    This adapter handles conversion between Mosaico Media objects and LangChain Documents.
    """

    @staticmethod
    def to_external(media: Media) -> Document:
        """
        Convert Media to LangChain Document.

        :param media: The Mosaico media object to convert
        :return: A LangChain Document
        """
        try:
            from langchain_core.documents import Document
        except ImportError:
            raise ImportError("LangChain is not installed")

        metadata = media.metadata.copy()
        metadata.update(
            {
                "source": str(media.path) if media.path else None,
                "mime_type": media.mime_type,
                "media_id": media.id,
                "encoding": media.encoding,
            }
        )

        # Convert binary data using Blob adapter if needed
        if isinstance(media.data, bytes) or media.path is not None:
            try:
                blob = LangChainBlobMediaAdapter.to_external(media)
                metadata["blob"] = blob
            except (ValueError, NotImplementedError):
                pass

        return Document(page_content=media.to_string(), metadata=metadata)

    @staticmethod
    def from_external(doc: Document) -> Media:
        """
        Convert LangChain Document to Media.

        :param doc: The LangChain document to convert
        :return: A Mosaico Media object
        """
        metadata = doc.metadata.copy()

        # If we have a blob, use Blob adapter
        if "blob" in metadata:
            return LangChainBlobMediaAdapter.from_external(metadata["blob"])

        # Otherwise use the content
        return Media.from_data(
            data=doc.page_content,
            path=metadata.get("source"),
            mime_type=metadata.get("mime_type"),
            encoding=metadata.get("encoding", "utf-8"),
            metadata=metadata,
        )


class LangChainBlobMediaAdapter:
    """
    An adapter for LangChain blobs.

    This adapter handles conversion between Mosaico Media objects and LangChain Blobs.
    """

    @staticmethod
    def to_external(media: Media) -> Blob:
        """
        Convert Media to LangChain Blob.

        :param media: The Mosaico media object to convert
        :return: A LangChain Blob
        """
        try:
            from langchain_core.documents.base import Blob
        except ImportError:
            raise ImportError("LangChain is not installed")

        return Blob(
            data=media.to_bytes(),
            mimetype=media.mime_type or "application/octet-stream",
            metadata={
                "path": str(media.path) if media.path else None,
                "media_id": media.id,
                "encoding": media.encoding,
                **media.metadata,
            },
        )

    @staticmethod
    def from_external(blob: Blob) -> Media:
        """
        Convert LangChain Blob to Media.

        :param blob: The LangChain blob to convert
        :return: A Mosaico Media object
        """
        metadata = blob.metadata.copy() if blob.metadata else {}

        if "source" in metadata:
            return Media.from_path(
                metadata["source"],
                mime_type=blob.mimetype,
                encoding=metadata.get("encoding", "utf-8"),
                metadata=metadata,
            )

        if not blob.data:
            raise ValueError("Blob data is empty")

        return Media.from_data(
            data=blob.data,
            mime_type=blob.mimetype,
            encoding=metadata.get("encoding", "utf-8"),
            metadata=metadata,
        )
