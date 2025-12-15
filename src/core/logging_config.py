"""Logging configuration for the application.

Provides centralized logging setup with consistent formatting and log levels.
Configures root logger and suppresses verbose third-party library logs.

Callers:
    - All modules: Use get_logger(__name__) to obtain logger instances
    - main.py: Uses logging.basicConfig directly

Callees:
    - logging: Python standard library logging module
    - src.core.config: Uses get_settings() for log level configuration

Configuration:
    - Format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    - Date format: '%Y-%m-%d %H:%M:%S'
    - Output: sys.stdout
    - Suppressed loggers: boto3, botocore, urllib3 (set to WARNING)
"""

import logging
import sys
from typing import Optional

from .config import get_settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """Configure application-wide logging.

    Sets up the root logger with consistent formatting and handlers.
    Suppresses verbose third-party library logs (boto3, botocore, urllib3).

    Args:
        log_level: Optional log level override. Uses settings if not provided.
                  Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL

    Called by:
        - Application initialization code
        - Test fixtures for log control

    Example:
        >>> setup_logging('DEBUG')
        >>> logger = logging.getLogger(__name__)
        >>> logger.debug('This will be shown')
    """
    settings = get_settings()
    level = log_level or settings.LOG_LEVEL

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Set specific loggers
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.

    Creates or retrieves a logger using Python's logging hierarchy.
    Typically called with __name__ to create module-specific loggers.

    Args:
        name: Logger name, typically __name__ for module-level loggers

    Returns:
        logging.Logger: Configured logger instance for the given name

    Called by:
        - All application modules for obtaining logger instances

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info('Processing started')
        >>> logger.error('Error occurred', exc_info=True)
    """
    return logging.getLogger(name)
