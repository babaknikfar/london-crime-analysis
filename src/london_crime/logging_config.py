"""
Logging configuration for London Crime Analysis project.

This module provides a centralized logging setup that reads
configuration from config.yaml and exposes a get_logger() helper
for consistent logging across all project modules.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


# Module-level flag to ensure logging is configured only once
_LOGGING_CONFIGURED = False

def _configure_logging() -> None:
    """
    Configure the root logger with console and file handlers.
    
    Reads settings from the global config object. This function is
    idempotent — calling it multiple times has no additional effect.
    """
    from london_crime.config import config

    global _LOGGING_CONFIGURED

    if _LOGGING_CONFIGURED:
        return

    # --- Read settings from config ---
    log_level_name: str = config.logging.get("level", "INFO")
    log_format: str = config.logging.get(
        "format",
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )
    log_file_relative: str = config.logging.get("file", "logs/london_crime.log")

    # Resolve the log file path relative to project root
    log_file: Path = config.paths.project_root / log_file_relative
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Convert string level name (e.g. "INFO") to logging constant
    log_level: int = getattr(logging, log_level_name.upper(), logging.INFO)

    # --- Build formatter ---
    formatter = logging.Formatter(log_format)

    # --- Build console handler ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # --- Build file handler ---
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # --- Configure root logger ---
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove any pre-existing handlers to avoid duplicate messages
    root_logger.handlers.clear()

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    _LOGGING_CONFIGURED = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Retrieve a configured logger.
    
    Args:
        name: Logger name — typically pass __name__ from the calling module.
              If None, returns the root logger.
    
    Returns:
        A logging.Logger instance configured with console and file handlers.
    """

    _configure_logging()
    return logging.getLogger(name)
