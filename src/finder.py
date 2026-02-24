"""
finder.py
=========
Locates the FiveM.exe regardless of where the user installed the game.

Detection is attempted in the following order (first hit wins):

  1. Default path   – %LOCALAPPDATA%\\FiveM\\FiveM.exe
  2. Registry       – fivem:// URL-protocol handler written by the installer
  3. Common paths   – a curated list of popular alternative install locations
  4. Desktop link   – resolves the target of a FiveM.lnk shortcut on the desktop
  5. Manual input   – prompts the user to type the path (3 attempts)

If every strategy fails the function returns None and the caller is responsible
for handling the missing installation gracefully.
"""

import os
import subprocess
import winreg
from pathlib import Path
from typing import Callable, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Alternative root directories to probe in strategy 3
# ---------------------------------------------------------------------------
_COMMON_ROOTS: List[Path] = [
    Path("C:/FiveM"),
    Path("C:/Games/FiveM"),
    Path("C:/Program Files/FiveM"),
    Path("C:/Program Files (x86)/FiveM"),
    Path("D:/FiveM"),
    Path("D:/Games/FiveM"),
    Path("E:/FiveM"),
    Path("E:/Games/FiveM"),
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def find_fivem_exe() -> Optional[Path]:
    """
    Try every detection strategy in order and return the first valid path.

    Returns
    -------
    Path | None
        Absolute path to a confirmed FiveM.exe, or None if not found.
    """
    # Each entry: (human-readable label, callable returning Path | None)
    strategies: List[Tuple[str, Callable[[], Optional[Path]]]] = [
        ("default path",       _find_via_default_path),
        ("registry",           _find_via_registry),
        ("common directories", _find_via_common_paths),
        ("desktop shortcut",   _find_via_desktop_shortcut),
    ]

    for label, strategy in strategies:
        path = strategy()
        if path and path.exists():
            print(f"  [FOUND] Located via {label}:")
            print(f"          {path}")
            return path

    # Nothing worked automatically – fall back to manual entry.
    return _ask_user_for_path()


# ---------------------------------------------------------------------------
# Strategy 1 – default installation path
# ---------------------------------------------------------------------------

def _find_via_default_path() -> Optional[Path]:
    """
    Check the standard installation location used by the FiveM installer.

    Default: %LOCALAPPDATA%\\FiveM\\FiveM.exe
    """
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    candidate = Path(local_app_data) / "FiveM" / "FiveM.exe"
    return candidate if candidate.exists() else None


# ---------------------------------------------------------------------------
# Strategy 2 – Windows Registry (fivem:// URL protocol handler)
# ---------------------------------------------------------------------------

def _find_via_registry() -> Optional[Path]:
    """
    Read the fivem:// URL-protocol entry written to the registry by the
    FiveM installer.  This key exists regardless of the chosen install path.

    Registry location::

        HKEY_CLASSES_ROOT\\fivem\\shell\\open\\command  →  "C:\\...\\FiveM.exe" "%1"

    The value is split on the quote character to extract only the executable
    path; the trailing  "%1"  placeholder is discarded.
    """
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"fivem\shell\open\command") as key:
            # QueryValueEx returns (value, type); we only need the value string.
            raw_value, _ = winreg.QueryValueEx(key, "")

            # Format: "C:\path\to\FiveM.exe" "%1"
            # Split on " to isolate the path between the first pair of quotes.
            parts = raw_value.split('"')
            if len(parts) < 2:
                return None

            exe_path = Path(parts[1])
            return exe_path if exe_path.exists() else None

    except (FileNotFoundError, OSError, IndexError):
        # Key does not exist or cannot be read – not a fatal error.
        return None


# ---------------------------------------------------------------------------
# Strategy 3 – probe common alternative install locations
# ---------------------------------------------------------------------------

def _find_via_common_paths() -> Optional[Path]:
    """
    Iterate over a hard-coded list of directories where players often install
    FiveM outside of the default AppData location (e.g. on a second drive).
    """
    for root in _COMMON_ROOTS:
        candidate = root / "FiveM.exe"
        if candidate.exists():
            return candidate
    return None


# ---------------------------------------------------------------------------
# Strategy 4 – desktop shortcut (.lnk)
# ---------------------------------------------------------------------------

def _find_via_desktop_shortcut() -> Optional[Path]:
    """
    Resolve the target path of a FiveM.lnk shortcut on the user's desktop.

    Uses PowerShell's WScript.Shell COM object to read the shortcut – no
    third-party Python libraries are required for this approach.
    """
    desktop = Path(os.environ.get("USERPROFILE", "")) / "Desktop" / "FiveM.lnk"
    if not desktop.exists():
        return None

    ps_command = (
        f'(New-Object -ComObject WScript.Shell)'
        f'.CreateShortcut("{desktop}").TargetPath'
    )

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=5,
        )
        target = Path(result.stdout.strip())
        return target if target.exists() else None

    except Exception:
        # PowerShell unavailable or shortcut unreadable – silently skip.
        return None


# ---------------------------------------------------------------------------
# Strategy 5 – manual user input (last resort)
# ---------------------------------------------------------------------------

def _ask_user_for_path() -> Optional[Path]:
    """
    Prompt the user to enter the full path to FiveM.exe by hand.

    Gives three attempts before returning None so the caller can decide how
    to handle a completely unresolvable installation.
    """
    print()
    print("  [WARN] FiveM could not be located automatically.")
    print("         Please enter the full path to FiveM.exe.")
    print(r'         Example: D:\Games\FiveM\FiveM.exe')
    print()

    for attempt in range(1, 4):
        try:
            raw = input(f"  Path (attempt {attempt}/3): ").strip().strip('"')
        except (EOFError, KeyboardInterrupt):
            # Non-interactive environment or user pressed Ctrl+C.
            break

        if not raw:
            continue

        candidate = Path(raw)
        if candidate.exists() and candidate.suffix.lower() == ".exe":
            return candidate

        print("  [ERROR] File not found – please check the path and try again.")

    return None
