class MosaicoException(Exception):
    """Base exception for all exceptions raised by Mosaico."""


class AssetNotFoundError(MosaicoException):
    """Raised when an asset could not be found in the project."""

    def __init__(self, asset_id: str) -> None:
        self.asset_id = asset_id

    def __str__(self) -> str:
        return f"Asset with ID '{self.asset_id}' not found in the project assets."


class TimelineEventNotFoundError(IndexError, MosaicoException):
    """Raised when a timeline could not be found in the project."""

    def __init__(self) -> None:
        super().__init__("Timeline event index out of range.")


class InvalidAssetTypeError(TypeError, MosaicoException):
    """Raised when an assets type is not supported."""

    def __init__(self, invalid_type: str) -> None:
        super().__init__(f"Invalid asset type: '{invalid_type}'")
