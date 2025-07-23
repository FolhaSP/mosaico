import os
import tempfile
from pathlib import Path
from typing import Any

from pydantic.fields import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from mosaico.types import LogLevel


class Settings(BaseSettings):
    """
    Settings for the Mosaico framework.
    """

    log_level: LogLevel = "INFO"
    """Log level for the application."""

    storage_options: dict[str, Any] = Field(default_factory=dict)
    """Default storage options for easy sharing between media/assets."""

    temp_dir: str | None = None
    """Custom temporary directory path. If None, uses system default with fallbacks."""

    model_config = SettingsConfigDict(env_prefix="MOSAICO_", env_nested_delimiter="__", validate_assignment=True)

    @property
    def resolved_temp_dir(self) -> str:
        """
        Get the resolved temporary directory to use for Mosaico operations.

        Tries in order:
        1. Custom temp_dir from settings
        2. System temp directory
        3. Current working directory
        4. User's home directory

        :returns: Path to usable temporary directory
        :raises RuntimeError: If no writable directory can be found
        """
        # Try custom temp directory first
        if self.temp_dir:
            temp_path = Path(self.temp_dir)
            if temp_path.exists() and os.access(temp_path, os.W_OK):
                return str(temp_path)

        # Fallback hierarchy
        fallback_dirs = [
            tempfile.gettempdir(),  # System temp
            os.getcwd(),  # Current directory
            Path.home(),  # User home
        ]

        for temp_dir in fallback_dirs:
            try:
                temp_path = Path(temp_dir)
                if temp_path.exists() and os.access(temp_path, os.W_OK):
                    return str(temp_path)
            except (OSError, PermissionError):
                continue

        raise RuntimeError("No writable temporary directory found")


settings = Settings()
"""Mosaico default settings instance."""
