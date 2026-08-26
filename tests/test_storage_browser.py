from pathlib import Path

import pytest

from app.services.storage_browser import StorageBrowser


def test_roots_returns_available_storage(tmp_path: Path):
    browser = StorageBrowser()
    roots = browser.roots()
    assert isinstance(roots, list)
    assert len(roots) > 0
    assert "mount_path" in roots[0]
    assert "display_name" in roots[0]


def test_prepare_disk_creates_directory_structure(tmp_path: Path):
    target = tmp_path / "downloads"
    browser = StorageBrowser()
    result = browser.prepare_disk(str(target))
    
    assert Path(result["download_dir"]).exists()
    assert Path(result["temp_dir"]).exists()
    assert (Path(result["download_dir"]) / "movies").is_dir()
    assert (Path(result["download_dir"]) / "documents").is_dir()
