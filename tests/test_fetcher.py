# tests/test_fetcher.py

import pytest
from pathlib import Path
import tempfile

from kagglefetcher.core import KaggleFetcher, fetch_dataset
from kagglefetcher.exceptions import DownloadError, MoveError, CleanupError


class DummyKHub:
    """Dummy kagglehub replacement for testing."""
    @staticmethod
    def dataset_download(source):
        # Simulate a "download" by creating a dummy temp directory
        temp = tempfile.mkdtemp(prefix="dummy_kaggle_dl_")
        return temp

@pytest.fixture(autouse=True)
def patch_khub(monkeypatch):
    # Patch kagglehub in core to prevent real network/downloads
    import kagglefetcher.core as coremod
    monkeypatch.setattr(coremod, "khub", DummyKHub)
    yield

def test_download_creates_dummy_dir(tmp_path):
    fetcher = KaggleFetcher("user/dataset", dest_base_dir=tmp_path)
    cache_path = fetcher.download()
    assert Path(cache_path).exists()
    # Clean up the dummy dir
    fetcher.cleanup(cache_path)

def test_move_and_cleanup(tmp_path):
    fetcher = KaggleFetcher("user/dataset", dest_base_dir=tmp_path)
    orig = fetcher.download()
    dest = fetcher.move(orig)
    assert Path(dest).exists()
    assert not Path(orig).exists()
    # Cleanup: remove destination
    fetcher.cleanup(dest)
    assert not Path(dest).exists()

def test_fetch_full_workflow(tmp_path):
    fetcher = KaggleFetcher("user/dataset", dest_base_dir=tmp_path)
    dest = fetcher.fetch()
    assert dest.exists()
    # Destination cleaned up for next test
    fetcher.cleanup(dest)

def test_fetch_dataset_one_liner(tmp_path):
    # Test the one-off function
    dest = fetch_dataset("user/dataset", dest_dir=tmp_path)
    assert Path(dest).exists()

def test_custom_exception_on_move(monkeypatch, tmp_path):
    # Simulate move failure, raise MoveError
    fetcher = KaggleFetcher("user/dataset", dest_base_dir=tmp_path)
    orig = fetcher.download()
    monkeypatch.setattr("shutil.move", lambda *a, **kw: (_ for _ in ()).throw(OSError("move failure")))
    with pytest.raises(MoveError):
        fetcher.move(orig)
    fetcher.cleanup(orig)

