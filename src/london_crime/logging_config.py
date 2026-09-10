"""
Logging configuration for London Crime Analysis project.

This module provides a centralized, reusable logging setup.
It is intentionally decoupled from the config module — settings
are passed in as parameters so that this module can be imported
from anywhere without circular-import issues.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


_LOGGING_CONFIGURED = False


def configure_logging(
    log_file: Path,
    level: str = "INFO",
    log_format: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
) -> None:
    """
    Configure the root logger with console and file handlers.

    Args:
        log_file: Absolute path to the log file. Parent directories
                  will be created if they don't exist.
        level: Log level name (e.g. "INFO", "DEBUG"). Defaults to "INFO".
        log_format: Format string for log records.

    This function is idempotent — calling it multiple times has no
    additional effect.
    """
    global _LOGGING_CONFIGURED

    if _LOGGING_CONFIGURED:
        return

    log_file.parent.mkdir(parents=True, exist_ok=True)

    log_level: int = getattr(logging, level.upper(), logging.INFO)

    formatter = logging.Formatter(log_format)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    _LOGGING_CONFIGURED = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Retrieve a logger by name.

    Note: The root logger must be configured separately via
    configure_logging() before logs will appear in console/file.

    Args:
        name: Logger name — typically pass __name__ from the calling module.
              If None, returns the root logger.

    Returns:
        A logging.Logger instance.
    """
    return logging.getLogger(name)