"""
FiveM Cache Cleaner
===================
Author      : maxionice
Repository  : https://github.com/maxionice/Clean-Fivem-Cache

A lightweight, no-install tool that:
  1. Locates the FiveM installation (even non-standard paths)
  2. Safely deletes only the cache folders that cause issues
  3. Relaunches FiveM automatically

Usage
-----
Double-click FiveM_Cache_Cleaner.exe  -- or run this script directly:

    python main.py
"""

import sys
import time

from src.finder   import find_fivem_exe
from src.cleaner  import get_app_dir, clear_cache
from src.launcher import launch_fivem


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------

def _print_header() -> None:
    """Print a decorative header to the console window."""
    print()
    print("=" * 52)
    print("      FiveM Cache Cleaner  |  by maxionice")
    print("=" * 52)
    print()


def _wait_and_exit(seconds: int, code: int = 0) -> None:
    """
    Show a closing countdown and exit with the given return code.

    Parameters
    ----------
    seconds : int
        Number of seconds to display before exiting.
    code : int
        Process exit code (0 = success, non-zero = error).
    """
    print()
    print(f"  This window will close in {seconds} seconds...")
    time.sleep(seconds)
    sys.exit(code)


# ---------------------------------------------------------------------------
# Main routine
# ---------------------------------------------------------------------------

def main() -> None:
    """Orchestrate the three-step clean-and-launch workflow."""
    _print_header()

    # ------------------------------------------------------------------
    # Step 1 - Locate FiveM
    # ------------------------------------------------------------------
    print("[ Step 1/3 ]  Locating FiveM installation...")
    print()

    exe_path = find_fivem_exe()

    if exe_path is None:
        print()
        print("  [FATAL] FiveM could not be found on this system.")
        print("          Please install FiveM and try again.")
        _wait_and_exit(5, code=1)

    # ------------------------------------------------------------------
    # Step 2 - Clean cache
    # ------------------------------------------------------------------
    print()
    print("[ Step 2/3 ]  Cleaning cache folders...")
    print()

    app_dir = get_app_dir(exe_path)
    success = clear_cache(app_dir)
    print()

    if not success:
        print("  Some folders could not be deleted.")
        print("  Close FiveM completely and run this tool again.")
        _wait_and_exit(5, code=1)

    print("  Cache cleaned successfully!")

    # ------------------------------------------------------------------
    # Step 3 - Relaunch FiveM
    # ------------------------------------------------------------------
    print()
    print("[ Step 3/3 ]  Starting FiveM...")

    if launch_fivem(exe_path):
        print("  FiveM is launching - have fun!")
    else:
        print("  Auto-launch failed. Please start FiveM manually.")

    _wait_and_exit(3)


if __name__ == "__main__":
    main()
