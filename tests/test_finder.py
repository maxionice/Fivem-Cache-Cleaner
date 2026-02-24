"""
tests/test_finder.py
====================
Unit tests for src/finder.py

All OS interactions (registry, filesystem, subprocess) are mocked so the
tests run on any machine – with or without FiveM installed.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.finder import (
    _find_via_common_paths,
    _find_via_default_path,
    _find_via_desktop_shortcut,
    _find_via_registry,
    find_fivem_exe,
)


class TestFindViaDefaultPath(unittest.TestCase):
    """_find_via_default_path() must return the path only if the file exists."""

    def test_returns_path_when_exe_exists(self) -> None:
        fake_exe = Path(r"C:\Users\Test\AppData\Local\FiveM\FiveM.exe")
        with patch("src.finder.Path.exists", return_value=True):
            result = _find_via_default_path()
        self.assertIsNotNone(result)

    def test_returns_none_when_exe_missing(self) -> None:
        with patch("src.finder.Path.exists", return_value=False):
            result = _find_via_default_path()
        self.assertIsNone(result)


class TestFindViaRegistry(unittest.TestCase):
    """_find_via_registry() must correctly parse the fivem:// command value."""

    def test_returns_path_from_registry(self) -> None:
        fake_exe = Path(r"D:\Games\FiveM\FiveM.exe")

        mock_key = MagicMock()
        mock_key.__enter__ = MagicMock(return_value=mock_key)
        mock_key.__exit__ = MagicMock(return_value=False)

        with patch("src.finder.winreg.OpenKey", return_value=mock_key), \
             patch("src.finder.winreg.QueryValueEx",
                   return_value=(f'"{fake_exe}" "%1"', 1)), \
             patch.object(Path, "exists", return_value=True):
            result = _find_via_registry()

        self.assertEqual(result, fake_exe)

    def test_returns_none_when_key_missing(self) -> None:
        with patch("src.finder.winreg.OpenKey", side_effect=FileNotFoundError):
            result = _find_via_registry()
        self.assertIsNone(result)

    def test_returns_none_when_exe_does_not_exist(self) -> None:
        mock_key = MagicMock()
        mock_key.__enter__ = MagicMock(return_value=mock_key)
        mock_key.__exit__ = MagicMock(return_value=False)

        with patch("src.finder.winreg.OpenKey", return_value=mock_key), \
             patch("src.finder.winreg.QueryValueEx",
                   return_value=('"C:\\FiveM\\FiveM.exe" "%1"', 1)), \
             patch.object(Path, "exists", return_value=False):
            result = _find_via_registry()
        self.assertIsNone(result)


class TestFindViaCommonPaths(unittest.TestCase):
    """_find_via_common_paths() must scan well-known directories."""

    def test_returns_first_existing_path(self) -> None:
        def _fake_exists(self: Path) -> bool:
            # Only pretend D:/FiveM/FiveM.exe exists.
            return str(self) == str(Path("D:/FiveM/FiveM.exe"))

        with patch.object(Path, "exists", _fake_exists):
            result = _find_via_common_paths()

        self.assertEqual(result, Path("D:/FiveM/FiveM.exe"))

    def test_returns_none_when_nothing_found(self) -> None:
        with patch.object(Path, "exists", return_value=False):
            result = _find_via_common_paths()
        self.assertIsNone(result)


class TestFindViaDesktopShortcut(unittest.TestCase):
    """_find_via_desktop_shortcut() must resolve the .lnk target via PowerShell."""

    def test_returns_none_when_lnk_missing(self) -> None:
        with patch.object(Path, "exists", return_value=False):
            result = _find_via_desktop_shortcut()
        self.assertIsNone(result)

    def test_returns_path_from_powershell(self) -> None:
        import subprocess

        fake_target = r"D:\Games\FiveM\FiveM.exe"
        mock_result = MagicMock()
        mock_result.stdout = fake_target + "\n"

        def _exists(self: Path) -> bool:
            p = str(self)
            return "Desktop" in p or p == fake_target

        with patch("src.finder.subprocess.run", return_value=mock_result), \
             patch.object(Path, "exists", _exists):
            result = _find_via_desktop_shortcut()

        self.assertEqual(result, Path(fake_target))


class TestFindFivemExe(unittest.TestCase):
    """find_fivem_exe() integration: returns first successful strategy."""

    def test_returns_default_path_when_available(self) -> None:
        fake = Path(r"C:\Users\Test\AppData\Local\FiveM\FiveM.exe")

        with patch("src.finder._find_via_default_path", return_value=fake), \
             patch.object(Path, "exists", return_value=True):
            result = find_fivem_exe()

        self.assertEqual(result, fake)

    def test_falls_through_to_registry_when_default_missing(self) -> None:
        fake = Path(r"D:\Games\FiveM\FiveM.exe")

        with patch("src.finder._find_via_default_path", return_value=None), \
             patch("src.finder._find_via_registry",     return_value=fake), \
             patch.object(Path, "exists", return_value=True):
            result = find_fivem_exe()

        self.assertEqual(result, fake)

    def test_returns_none_when_all_strategies_fail(self) -> None:
        with patch("src.finder._find_via_default_path",   return_value=None), \
             patch("src.finder._find_via_registry",        return_value=None), \
             patch("src.finder._find_via_common_paths",    return_value=None), \
             patch("src.finder._find_via_desktop_shortcut",return_value=None), \
             patch("src.finder._ask_user_for_path",        return_value=None):
            result = find_fivem_exe()

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
