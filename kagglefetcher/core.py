import kagglehub as khub
import shutil
import logging
import os
from pathlib import Path
from typing import Optional, Union
from urllib3.exceptions import NotOpenSSLWarning
import warnings

from .exceptions import DownloadError, MoveError, CleanupError

warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# Create a module-level logger with a unique name
logger = logging.getLogger(__name__)


class KaggleFetcher:
    """
    A flexible wrapper around kagglehub for downloading and managing Kaggle datasets.
    
    Args:
        source: Kaggle dataset identifier (e.g., 'username/dataset-name')
        dest_base_dir: Base directory for storing datasets (default: './kaggle/input')
        enable_logging: Enable file-based logging (default: False)
        log_dir: Directory for log files (default: './logs')
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
        
        # Set default destination directory
        if dest_base_dir is None:
            dest_base_dir = Path.cwd() / "kaggle" / "input"
        self.dest_base_dir = Path(dest_base_dir)
        self.dest_path = self.dest_base_dir / self.dataset_name
        
        # Configure logging if enabled
        if enable_logging:
            self._setup_logging(log_dir or Path("logs"))
    
    def _setup_logging(self, log_dir: Path) -> None:
        """Configure file-based logging."""
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / "kaggle_fetcher.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
    
    def download(self) -> Path:
        """
        Download the dataset from Kaggle.
        
        Returns:
            Path: The path where the dataset is cached.
            
        Raises:
            DownloadError: If download fails.
        """
        try:
            logger.info(f"Downloading dataset: {self.source}")
            cache_path = khub.dataset_download(self.source)
            logger.info(f"Dataset downloaded to: {cache_path}")
            return Path(cache_path)
        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise DownloadError(f"Failed to download {self.source}: {e}") from e
    
    def move(self, cache_path: Path, dest_path: Optional[Path] = None) -> Path:
        """
        Move the downloaded dataset to the destination directory.
        
        Args:
            cache_path: Source path of the downloaded dataset
            dest_path: Destination path (uses self.dest_path if None)
            
        Returns:
            Path: The final destination path.
            
        Raises:
            MoveError: If move operation fails.
        """
        dest = dest_path or self.dest_path
        
        try:
            logger.info(f"Moving dataset from {cache_path} to {dest}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            
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
        """
        Remove the cached dataset files.
        
        Args:
            cache_path: Path to the cached dataset
            
        Returns:
            bool: True if cleanup was successful.
            
        Raises:
            CleanupError: If cleanup fails.
        """
        try:
            logger.info(f"Cleaning up cache: {cache_path}")
            if Path(cache_path).exists():
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
        """
        Download, move, and optionally clean up the Kaggle dataset.
        
        Args:
            keep_cache: Whether to keep the original cache after moving
            dest_path: Custom destination path (uses self.dest_path if None)
            
        Returns:
            Path: The final destination path of the dataset.
            
        Raises:
            DownloadError: If download fails.
            MoveError: If move fails.
        """
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
    **kwargs
) -> Path:
    """
    Convenience function to fetch a Kaggle dataset in one call.
    
    Args:
        source: Kaggle dataset identifier
        dest_dir: Destination base directory
        **kwargs: Additional arguments passed to KaggleFetcher
        
    Returns:
        Path: The path to the downloaded dataset.
        
    Example:
        >>> from kaggle_fetcher import fetch_dataset
        >>> path = fetch_dataset("username/dataset-name")
        >>> print(f"Dataset saved to: {path}")
    """
    fetcher = KaggleFetcher(source, dest_base_dir=dest_dir, **kwargs)
    return fetcher.fetch()
