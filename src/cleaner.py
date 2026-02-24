"""
cleaner.py
==========
Deletes the FiveM cache directories that accumulate corrupted or stale data.

Only the following sub-folders inside FiveM.app are targeted:

  - cache             →  general game asset cache
  - server-cache      →  server-specific resource cache
  - server-cache-priv →  private/signed server-resource cache

The ``game-storage`` folder is intentionally excluded because it contains
the bulk of the downloaded game files (~multi-GB).  Deleting it would force
players to re-download FiveM from scratch, which is never the desired outcome.
"""

import shutil
from pathlib import Path
from typing import List


# ---------------------------------------------------------------------------
# Configuration – the only folders this tool is allowed to delete
# ---------------------------------------------------------------------------

CACHE_FOLDERS: List[str] = [
    "cache",
    "server-cache",
    "server-cache-priv",
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_app_dir(fivem_exe: Path) -> Path:
    """
    Derive the FiveM.app directory from the executable's location.

    The app folder always sits next to FiveM.exe::

        <install_dir>/FiveM.exe
        <install_dir>/FiveM.app/cache/
        <install_dir>/FiveM.app/server-cache/
        <install_dir>/FiveM.app/server-cache-priv/
        <install_dir>/FiveM.app/game-storage/   ← never touched

    Parameters
    ----------
    fivem_exe : Path
        Confirmed path to FiveM.exe.

    Returns
    -------
    Path
        Path to the FiveM.app directory (may or may not exist yet).
    """
    return fivem_exe.parent / "FiveM.app"


def clear_cache(app_dir: Path) -> bool:
    """
    Iterate over ``CACHE_FOLDERS`` and remove each one that exists.

    Parameters
    ----------
    app_dir : Path
        The FiveM.app directory that contains the cache sub-folders.

    Returns
    -------
    bool
        True  – all present folders were removed without errors.
        False – at least one folder could not be deleted (error logged to stdout).
    """
    if not app_dir.exists():
        print(f"  [ERROR] FiveM.app directory not found:")
        print(f"          {app_dir}")
        print("          Launch FiveM at least once to create this folder,")
        print("          then run this tool again.")
        return False

    overall_success = True

    for folder_name in CACHE_FOLDERS:
        folder_path = app_dir / folder_name

        if not folder_path.exists():
            # Already absent – nothing to do, not an error.
            print(f"  [SKIP]  {folder_name:<30} (already absent)")
            continue

        if _delete_folder(folder_path):
            print(f"  [OK]    {folder_name:<30} deleted")
        else:
            overall_success = False

    return overall_success


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _delete_folder(path: Path) -> bool:
    """
    Recursively remove a directory tree and all of its contents.

    Parameters
    ----------
    path : Path
        Directory to delete.

    Returns
    -------
    bool
        True on success, False if an OS or permission error occurs.
    """
    try:
        shutil.rmtree(path)
        return True
    except PermissionError:
        print(f"  [ERROR] Permission denied – could not delete '{path.name}'.")
        print("          Make sure FiveM is fully closed and try again.")
    except OSError as exc:
        print(f"  [ERROR] OS error while deleting '{path.name}': {exc}")
    return False
