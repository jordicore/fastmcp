"""Logging utilities for FastMCP."""

import logging
from typing import Literal

from rich.logging import RichHandler


def get_logger(name: str) -> logging.Logger:
    """Get a logger nested under fastmcp namespace.

    Args:
        name: the name of the logger, which will be prefixed with 'fastmcp.'

    Returns:
        a configured logger instance
    """
    return logging.getLogger(f"fastmcp.{name}")


def configure_logging(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
) -> None:
    """Configure logging for FastMCP.

    Args:
        level: the log level to use
    """
    logging.basicConfig(
        level=level, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)]
    )
