from typing import Any

from pydantic.fields import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings for the Mosaico framework.
    """

    storage_options: dict[str, Any] = Field(default_factory=dict)
    """Default storage options for easy sharing between media/assets."""

    model_config = SettingsConfigDict(env_file="mosaico_", env_nested_delimiter="__")


settings = Settings()
"""Mosaico default settings instance."""
