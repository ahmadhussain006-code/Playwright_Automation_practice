"""
utils/logger.py
───────────────
Centralised logger factory used by every page object and test.

Usage:
    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Navigating to home page")
"""

import logging
import os
from datetime import datetime


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger.

    The root handler is configured only once (idempotent), so calling
    get_logger() multiple times does NOT add duplicate handlers.

    Args:
        name: Typically ``__name__`` from the calling module.

    Returns:
        A configured ``logging.Logger`` instance.
    """
    logger = logging.getLogger(name)

    # Only add handlers once (prevents duplicate log lines in long runs)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # ── Console handler (INFO and above) ─────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter(
        fmt="%(asctime)s  [%(levelname)-8s]  %(name)s  –  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_fmt)

    # ── File handler (DEBUG and above, written to reports/) ──────────────────
    os.makedirs("reports", exist_ok=True)
    log_filename = os.path.join(
        "reports",
        f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    )
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        fmt="%(asctime)s  [%(levelname)-8s]  %(name)s  –  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_fmt)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger