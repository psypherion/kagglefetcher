"""
Kaggle Fetcher - A flexible wrapper around kagglehub.

Simple usage:
    >>> from kagglefetcher import fetch_dataset
    >>> path = fetch_dataset("username/dataset-name")
    
Advanced usage:
    >>> from kagglefetcher import KaggleFetcher
    >>> fetcher = KaggleFetcher(
    ...     source="username/dataset-name",
    ...     dest_base_dir="./data",
    ...     enable_logging=True
    ... )
    >>> path = fetcher.fetch()
"""

from .core import KaggleFetcher, fetch_dataset
from .exceptions import (
    KaggleFetcherError,
    DownloadError,
    MoveError,
    CleanupError
)

__version__ = "0.1.0"
__all__ = [
    "KaggleFetcher",
    "fetch_dataset",
    "KaggleFetcherError",
    "DownloadError",
    "MoveError",
    "CleanupError",
]
