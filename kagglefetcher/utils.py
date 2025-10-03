"""
utils.py - Helper functions for kaggle_fetcher.
"""

import os
from pathlib import Path
import logging

def ensure_dir(path: str | Path):
    """
    Ensure that a directory exists. Create it if it doesn't.

    Args:
        path (str or Path): Path to the directory.

    Returns:
        Path: The Path object for the directory.
    """
    p = Path(path)
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)
    return p

def clean_path(path: str | Path):
    """
    Normalize and expand a path string.

    Args:
        path (str or Path): A path string or Path object.

    Returns:
        Path: Normalized and expanded Path object.
    """
    return Path(os.path.expanduser(os.path.abspath(str(path))))

def setup_logger(log_dir: str = "logs", log_file: str = "kagglefetcher.log", module_name: str | None = None):
    """
    Setup logging for a module (file and stream).

    Args:
        log_dir (str): Directory to store log files.
        log_file (str): File name for logging.
        module_name (str or None): Logger name (None for root).

    Returns:
        logging.Logger: Configured logger.
    """
    ensure_dir(log_dir)
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(Path(log_dir) / log_file)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
    
    return logger
