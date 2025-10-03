import kagglehub as khub
import shutil
import logging
import warnings
from pathlib import Path
from typing import Optional, Union, Any
from urllib3.exceptions import NotOpenSSLWarning

from .exceptions import DownloadError, MoveError, CleanupError
from .utils import ensure_dir, clean_path, setup_logger

warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# Create (or get) the module-level logger using utils
logger = logging.getLogger(__name__)

class KaggleFetcher:
    """
    A flexible wrapper around kagglehub for downloading and managing Kaggle datasets.
    """

    def __init__(
        self, 
        source: str,
        dest_base_dir: Optional[Union[str, Path]] = None,
        enable_logging: bool = False,
        log_dir: Optional[Union[str, Path]] = None
    ) -> None:
        self.source = source
        self.dataset_name = source.split("/")[-1]

        # Use utils for consistent path handling
        if dest_base_dir is None:
            dest_base_dir = Path.cwd() / "kaggle" / "input"
        self.dest_base_dir = clean_path(dest_base_dir)
        self.dest_path = self.dest_base_dir / self.dataset_name

        # Use logging setup from utils if needed
        if enable_logging:
            setup_logger(str(log_dir) if log_dir else "logs", "kaggle_fetcher.log", __name__)

    def download(self) -> Path:
        """Download the dataset from Kaggle."""
        try:
            logger.info(f"Downloading dataset: {self.source}")
            cache_path = khub.dataset_download(self.source)
            logger.info(f"Dataset downloaded to: {cache_path}")
            return clean_path(cache_path)
        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise DownloadError(f"Failed to download {self.source}: {e}") from e

    def move(self, cache_path: Path, dest_path: Optional[Path] = None) -> Path:
        """Move the downloaded dataset to the destination directory."""
        dest = clean_path(dest_path or self.dest_path)
        try:
            logger.info(f"Moving dataset from {cache_path} to {dest}")
            ensure_dir(dest.parent)
            if dest.exists():
                logger.warning(f"Destination {dest} already exists, removing it")
                shutil.rmtree(dest)
            shutil.move(str(cache_path), str(dest))
            logger.info("Dataset moved successfully")
            return dest
        except Exception as e:
            logger.error(f"Move failed: {e}")
            raise MoveError(f"Failed to move dataset: {e}") from e

    def cleanup(self, cache_path: Path) -> bool:
        """Remove the cached dataset files."""
        cache_path = clean_path(cache_path)
        try:
            logger.info(f"Cleaning up cache: {cache_path}")
            if cache_path.exists():
                shutil.rmtree(cache_path)
                logger.info("Cleanup successful")
                return True
            else:
                logger.warning(f"Cache path {cache_path} does not exist")
                return False
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            raise CleanupError(f"Failed to cleanup {cache_path}: {e}") from e

    def fetch(
        self, 
        keep_cache: bool = False,
        dest_path: Optional[Path] = None
    ) -> Path:
        """Download, move, and optionally clean up the Kaggle dataset."""
        cache_path = self.download()
        final_path = self.move(cache_path, dest_path)
        if not keep_cache and cache_path != final_path:
            try:
                self.cleanup(cache_path)
            except CleanupError as e:
                logger.warning(f"Cleanup failed but dataset was moved: {e}")
        return final_path

# Convenience function for one-liner usage
def fetch_dataset(
    source: str,
    dest_dir: Optional[Union[str, Path]] = None,
    **kwargs: Any
) -> Path:
    """Fetch a Kaggle dataset in one call."""
    fetcher = KaggleFetcher(source, dest_base_dir=dest_dir, **kwargs)
    return fetcher.fetch()
