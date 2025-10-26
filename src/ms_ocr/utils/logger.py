"""Structured logging configuration."""

import logging
import sys
from pathlib import Path
from typing import Optional

import structlog


def setup_logger(
    log_file: Optional[Path] = None, level: str = "INFO", json_logs: bool = False
) -> structlog.BoundLogger:
    """Configure structured logging.

    Args:
        log_file: Optional path to log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        json_logs: Whether to output logs as JSON

    Returns:
        Configured structlog logger
    """
    log_level = getattr(logging, level.upper())

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        logging.root.addHandler(file_handler)

    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.extend(
            [
                structlog.dev.ConsoleRenderer(colors=True),
            ]
        )

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()


def get_logger(name: str = "ms_ocr") -> structlog.BoundLogger:
    """Get a logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return structlog.get_logger(name)
