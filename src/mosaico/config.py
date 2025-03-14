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

    model_config = SettingsConfigDict(env_prefix="MOSAICO_", env_nested_delimiter="__", validate_assignment=True)


settings = Settings()
"""Mosaico default settings instance."""
