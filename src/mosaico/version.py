from importlib import metadata


try:
    __version__ = str(metadata.version("mosaico"))
except metadata.PackageNotFoundError:
    __version__ = "main"
