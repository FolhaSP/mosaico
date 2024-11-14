class MosaicoException(Exception):
    """Base exception for all exceptions raised by Mosaico."""

    pass


class InvalidAssetTypeError(TypeError, MosaicoException):
    """Raised when an assets type is not supported."""

    def __init__(self, invalid_type: str) -> None:
        super().__init__(f"Invalid asset type: {invalid_type}")
