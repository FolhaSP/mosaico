class MosaicoException(Exception):
    """Base exception for all exceptions raised by Mosaico."""

    ...


class AssetNotFoundError(MosaicoException):
    """Raised when an asset could not be found in the project."""

    def __init__(self, asset_id: str) -> None:
        self.asset_id = asset_id

    def __str__(self) -> str:
        return f"Asset with ID '{self.asset_id}' not found in the project assets."


class DuplicatedAssetError(MosaicoException):
    """Raised when a new asset already exists inside a project."""

    def __init__(self, asset_id: str) -> None:
        self.asset_id = asset_id

    def __str__(self) -> str:
        return f"Asset already exists in the project: {self.asset_id}"


class EmptyTimelineError(MosaicoException):
    """Raised when the when an operation could not be executed due to an empty timeline."""

    def __init__(self) -> None:
        super().__init__("Timeline is empty.")


class EmptyTrackError(MosaicoException):
    """Raised when the when an operation could not be executed due to an empty track."""

    def __init__(self) -> None:
        super().__init__("Track is empty.")


class EmptyAssetError(MosaicoException):
    """Raised when the when an operation could not be executed due to an empty asset."""

    def __init__(self) -> None:
        super().__init__("Asset is empty.")


class TrackNotFoundError(IndexError, MosaicoException):
    """Raised when a track could not be found in the project's timeline."""

    def __init__(self) -> None:
        super().__init__("Track index out of range.")


class InvalidAssetTypeError(TypeError, MosaicoException):
    """Raised when an assets type is not supported."""

    def __init__(self, invalid_type: str) -> None:
        super().__init__(f"Invalid asset type: '{invalid_type}'")
