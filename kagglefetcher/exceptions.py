"""Custom exceptions for kaggle-fetcher."""


class KaggleFetcherError(Exception):
    """Base exception for kaggle-fetcher."""
    pass


class DownloadError(KaggleFetcherError):
    """Raised when dataset download fails."""
    pass


class MoveError(KaggleFetcherError):
    """Raised when moving dataset fails."""
    pass


class CleanupError(KaggleFetcherError):
    """Raised when cleanup operation fails."""
    pass
