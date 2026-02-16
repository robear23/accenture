"""Structured logging with file and console handlers."""

import logging
import sys
from datetime import datetime

from job_assistant.config import LOG_DIR


def get_logger(name: str = "job_assistant") -> logging.Logger:
    """Get or create a logger with file and console handlers."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    from job_assistant.config import settings

    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    formatter = logging.Formatter(
        "%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # File handler (daily rotation)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"{datetime.now():%Y-%m-%d}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
