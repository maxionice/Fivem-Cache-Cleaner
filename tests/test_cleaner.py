"""
tests/test_cleaner.py
=====================
Unit tests for src/cleaner.py

A temporary mock directory is created in a system temp folder to simulate
the FiveM.app structure.  No real FiveM files are touched during testing.

Mock structure created per test::

    <tmpdir>/
    └── FiveM.app/
        ├── cache/
        │   └── dummy.txt
        ├── server-cache/
        │   └── dummy.txt
        ├── server-cache-priv/
        │   └── dummy.txt
        └── game-storage/          ← must NOT be deleted
            └── big_file.txt
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Make sure the project root is on sys.path so `from src.cleaner import ...`
# resolves correctly when tests are run from the tests/ sub-directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.cleaner import CACHE_FOLDERS, clear_cache, get_app_dir


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_mock_fivem(tmp_path: Path) -> tuple[Path, Path]:
    """
    Build a fake FiveM install tree inside tmp_path.

    Returns
    -------
    exe_path : Path   – simulated FiveM.exe (empty file)
    app_dir  : Path   – simulated FiveM.app directory
    """
    exe_path = tmp_path / "FiveM.exe"
    exe_path.touch()                            # create empty placeholder

    app_dir = tmp_path / "FiveM.app"
    app_dir.mkdir()

    # Create each cache folder with a dummy file inside.
    for name in CACHE_FOLDERS:
        folder = app_dir / name
        folder.mkdir()
        (folder / "dummy.txt").write_text("cache data")

    # Create game-storage – this must survive the cleaning process.
    game_storage = app_dir / "game-storage"
    game_storage.mkdir()
    (game_storage / "big_file.txt").write_text("important game data")

    return exe_path, app_dir


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGetAppDir(unittest.TestCase):
    """get_app_dir() must resolve the FiveM.app path from the exe location."""

    def test_app_dir_is_sibling_of_exe(self) -> None:
        exe = Path(r"C:\Games\FiveM\FiveM.exe")
        expected = Path(r"C:\Games\FiveM\FiveM.app")
        self.assertEqual(get_app_dir(exe), expected)

    def test_default_path(self) -> None:
        exe = Path(r"C:\Users\Player\AppData\Local\FiveM\FiveM.exe")
        expected = Path(r"C:\Users\Player\AppData\Local\FiveM\FiveM.app")
        self.assertEqual(get_app_dir(exe), expected)


class TestClearCache(unittest.TestCase):
    """clear_cache() must delete only the designated folders."""

    def setUp(self) -> None:
        """Create a fresh temporary directory for each test."""
        import tempfile, os
        self._tmp = tempfile.mkdtemp()
        self.tmp_path = Path(self._tmp)

    def tearDown(self) -> None:
        """Remove the temporary directory tree after each test."""
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    # ------------------------------------------------------------------
    # Happy path
    # ------------------------------------------------------------------

    def test_cache_folders_are_deleted(self) -> None:
        """All three cache folders must be gone after cleaning."""
        _, app_dir = _build_mock_fivem(self.tmp_path)

        result = clear_cache(app_dir)

        self.assertTrue(result, "clear_cache should return True on success")
        for name in CACHE_FOLDERS:
            self.assertFalse(
                (app_dir / name).exists(),
                f"Cache folder '{name}' should have been deleted",
            )

    def test_game_storage_is_preserved(self) -> None:
        """game-storage must NOT be touched under any circumstances."""
        _, app_dir = _build_mock_fivem(self.tmp_path)

        clear_cache(app_dir)

        game_storage = app_dir / "game-storage"
        self.assertTrue(game_storage.exists(), "game-storage must not be deleted")
        self.assertTrue(
            (game_storage / "big_file.txt").exists(),
            "Files inside game-storage must remain intact",
        )

    def test_already_absent_folders_are_skipped(self) -> None:
        """If a cache folder doesn't exist, clear_cache should still succeed."""
        _, app_dir = _build_mock_fivem(self.tmp_path)

        # Pre-remove one folder to simulate an already-clean state.
        import shutil
        shutil.rmtree(app_dir / "cache")

        result = clear_cache(app_dir)
        self.assertTrue(result, "Missing folder should be treated as already clean")

    def test_returns_true_when_all_folders_absent(self) -> None:
        """clear_cache on a completely clean app_dir should return True."""
        app_dir = self.tmp_path / "FiveM.app"
        app_dir.mkdir()
        # No cache folders at all – everything is already clean.

        result = clear_cache(app_dir)
        self.assertTrue(result)

    # ------------------------------------------------------------------
    # Error paths
    # ------------------------------------------------------------------

    def test_returns_false_when_app_dir_missing(self) -> None:
        """If FiveM.app does not exist, clear_cache must return False."""
        missing = self.tmp_path / "FiveM.app"
        # Do NOT create this directory.

        result = clear_cache(missing)
        self.assertFalse(result)

    def test_returns_false_on_permission_error(self) -> None:
        """If shutil.rmtree raises PermissionError the function returns False."""
        _, app_dir = _build_mock_fivem(self.tmp_path)

        with patch("src.cleaner.shutil.rmtree", side_effect=PermissionError("locked")):
            result = clear_cache(app_dir)

        self.assertFalse(result)

    def test_returns_false_on_os_error(self) -> None:
        """If shutil.rmtree raises a generic OSError the function returns False."""
        _, app_dir = _build_mock_fivem(self.tmp_path)

        with patch("src.cleaner.shutil.rmtree", side_effect=OSError("disk error")):
            result = clear_cache(app_dir)

        self.assertFalse(result)


class TestClearCacheOnlyTargetsFolders(unittest.TestCase):
    """Extra folders placed in FiveM.app must not be touched."""

    def setUp(self) -> None:
        import tempfile
        self._tmp = tempfile.mkdtemp()
        self.tmp_path = Path(self._tmp)

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_extra_folders_untouched(self) -> None:
        """Folders not in CACHE_FOLDERS must survive the cleaning process."""
        _, app_dir = _build_mock_fivem(self.tmp_path)

        # Add two extra folders that must not be deleted.
        extra_a = app_dir / "plugins"
        extra_b = app_dir / "logs"
        extra_a.mkdir()
        extra_b.mkdir()

        clear_cache(app_dir)

        self.assertTrue(extra_a.exists(), "'plugins' folder must not be deleted")
        self.assertTrue(extra_b.exists(), "'logs' folder must not be deleted")


if __name__ == "__main__":
    unittest.main(verbosity=2)
