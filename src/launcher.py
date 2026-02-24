"""
launcher.py
===========
Starts FiveM after the cache has been successfully cleaned.

The process is spawned with the Windows ``DETACHED_PROCESS`` creation flag
so that FiveM continues to run independently after this console window closes.
Without this flag the child process would be terminated together with this tool.
"""

import subprocess
from pathlib import Path


# Windows process-creation flag: child process has no attached console and
# is not terminated when its parent exits.
_DETACHED_PROCESS = 0x00000008


def launch_fivem(exe_path: Path) -> bool:
    """
    Start FiveM as a detached background process.

    Parameters
    ----------
    exe_path : Path
        Verified, existing path to FiveM.exe.

    Returns
    -------
    bool
        True  – process was spawned successfully.
        False – an OS error prevented the launch (error logged to stdout).
    """
    try:
        subprocess.Popen(
            [str(exe_path)],
            creationflags=_DETACHED_PROCESS,
        )
        return True
    except OSError as exc:
        print(f"  [ERROR] Could not launch FiveM: {exc}")
        return False
