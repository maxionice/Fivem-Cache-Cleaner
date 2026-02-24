"""
tests/test_launcher.py
======================
Unit tests for src/launcher.py

subprocess.Popen is mocked so no actual process is ever started during testing.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.launcher import launch_fivem


class TestLaunchFivem(unittest.TestCase):
    """launch_fivem() must start the process and return True on success."""

    _FAKE_EXE = Path(r"C:\Games\FiveM\FiveM.exe")

    def test_returns_true_on_success(self) -> None:
        with patch("src.launcher.subprocess.Popen") as mock_popen:
            result = launch_fivem(self._FAKE_EXE)

        self.assertTrue(result)
        mock_popen.assert_called_once()

    def test_passes_correct_exe_to_popen(self) -> None:
        with patch("src.launcher.subprocess.Popen") as mock_popen:
            launch_fivem(self._FAKE_EXE)

        args, kwargs = mock_popen.call_args
        self.assertIn(str(self._FAKE_EXE), args[0])

    def test_uses_detached_process_flag(self) -> None:
        """DETACHED_PROCESS (0x00000008) must be set so FiveM keeps running."""
        with patch("src.launcher.subprocess.Popen") as mock_popen:
            launch_fivem(self._FAKE_EXE)

        _, kwargs = mock_popen.call_args
        self.assertEqual(kwargs.get("creationflags"), 0x00000008)

    def test_returns_false_on_os_error(self) -> None:
        with patch("src.launcher.subprocess.Popen", side_effect=OSError("not found")):
            result = launch_fivem(self._FAKE_EXE)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
