import logging

from mosaico.config import settings
from mosaico.types import LogLevel


LOG_FORMAT = "%(asctime)s [%(levelname)8s] %(name)s %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.

    This will return a logger configured according to the Mosaico log settings.
    If a logger with the given name already exists, it will be returned.

    :param name: The name of the logger.
    :return: A logger instance.
    """
    logger = logging.getLogger(name)

    # Only configure if the logger doesn't have handlers already
    if not logger.handlers:
        # Set the log level
        level = _get_log_level(settings.log_level)
        logger.setLevel(level)

        # Set the formatter and handler
        formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.setLevel(level)

        # Add the handler to the logger
        logger.addHandler(handler)

    return logger


def configure_logging(level: LogLevel) -> None:
    """
    Configure the logging system.

    :param level: The logging level to set.
    """
    settings.log_level = level


def _get_log_level(level: LogLevel) -> int:
    """
    Get the logging level from the given string.
    """
    return getattr(logging, level.upper())
