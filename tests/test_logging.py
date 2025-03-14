import logging

import pytest
from pydantic import ValidationError

from mosaico.logging import configure_logging, get_logger
from mosaico.types import LogLevel


def test_get_logger():
    """Test that get_logger returns a properly configured logger."""
    logger = get_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"
    assert len(logger.handlers) > 0
    assert isinstance(logger.handlers[0], logging.StreamHandler)


def test_configure_logging():
    """Test that configure_logging updates the settings."""
    configure_logging("DEBUG")
    logger = get_logger("test_configure_logger")
    assert logger.level == logging.DEBUG

    # Reset to INFO for other tests
    configure_logging("INFO")


@pytest.mark.parametrize(
    "level_name,level_value",
    [
        ("DEBUG", logging.DEBUG),
        ("INFO", logging.INFO),
        ("WARNING", logging.WARNING),
        ("ERROR", logging.ERROR),
        ("CRITICAL", logging.CRITICAL),
    ],
)
def test_different_log_levels(level_name: LogLevel, level_value: int):
    """Test using different log levels."""
    configure_logging(level_name)
    logger = get_logger(f"test_level_{level_name}")
    assert logger.level == level_value


def test_invalid_log_level():
    """Test that an invalid log level raises a ValueError."""
    with pytest.raises(ValidationError, match="INVALID"):
        configure_logging(level="INVALID")


def test_no_duplicate_handlers():
    """Test that getting the same logger twice doesn't add duplicate handlers."""
    logger1 = get_logger("test_duplicate")
    initial_handler_count = len(logger1.handlers)

    # Get the same logger again
    logger2 = get_logger("test_duplicate")
    assert logger1 is logger2  # Same object
    assert len(logger2.handlers) == initial_handler_count  # No new handlers
