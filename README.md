# 🧹 FiveM Cache Cleaner

A lightweight, beginner-friendly tool that safely clears the FiveM cache with
just a double-click and automatically launches the game afterward.

Designed for players without technical experience – no manual folder navigation,
no accidental deletion of the wrong files.

---

## 🎯 For Server Owners & Support Teams

Link this tool in your `#faq` or `#support` channel.
When players report texture bugs, invisible objects, or endless loading screens –
point them here.  It drastically reduces support tickets.

---

## ✨ Features

| Feature | Details |
|---|---|
| **1-Click Solution** | No installation needed – just run the `.exe` |
| **Smart Detection** | Finds FiveM even if installed in a non-default location |
| **100% Safe** | Only deletes `cache`, `server-cache`, and `server-cache-priv` |
| **No Re-Download** | `game-storage` (your game files) is never touched |
| **Auto-Start** | FiveM relaunches automatically after cleaning |
| **No Admin Rights** | Runs with standard user permissions |

---

## 🚀 How to Use (Players)

1. Download **`FiveM_Cache_Cleaner.exe`** from the [Releases](../../releases) page.
2. Fully close FiveM (check the system tray).
3. Double-click the downloaded file.
4. A small window opens, cleans the cache, and restarts FiveM automatically.
5. Done – enjoy!

---

## 📍 FiveM Detection

The tool automatically finds FiveM regardless of install location:

1. **Default path** – `%LOCALAPPDATA%\FiveM\FiveM.exe`
2. **Registry** – reads the `fivem://` URL-protocol entry (most reliable)
3. **Common directories** – scans `D:\FiveM`, `D:\Games\FiveM`, etc.
4. **Desktop shortcut** – resolves the `.lnk` target path
5. **Manual input** – asks you to type the path if everything else fails

---

<details>
<summary>🗂️ Project Structure & Developer Info</summary>

### Project Structure

```
Fivem-Cache-Cleaner/
├── .github/
│   └── workflows/
│       └── build-release.yml   # Auto-builds .exe and publishes a Release on tag push
├── src/
│   ├── finder.py               # FiveM installation detection (5 strategies)
│   ├── cleaner.py              # Cache folder deletion logic
│   └── launcher.py             # Detached process launcher
├── tests/
│   ├── test_cleaner.py         # Unit tests for cleaner.py
│   ├── test_finder.py          # Unit tests for finder.py
│   └── test_launcher.py        # Unit tests for launcher.py
├── main.py                     # Entry point – orchestrates all three steps
├── build.bat                   # Local build script (runs PyInstaller)
├── requirements-dev.txt        # Dev dependencies (PyInstaller, pytest)
└── .gitignore
```

### Run locally

```bash
python main.py
```

### Run tests

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

### Build the .exe locally

```bat
build.bat
# Output: dist\FiveM_Cache_Cleaner.exe
```

### Publish a new release

```bash
git tag v1.2.3
git push origin v1.2.3
```

GitHub Actions will automatically build the `.exe` and attach it to a new Release.

</details>

---

## 🔒 Open Source & Transparent

The code is intentionally kept simple so any server owner or player can verify
that it performs **no malicious actions**.  It reads two paths, deletes three
folders, and launches one executable – nothing more.

---

*Developed by [maxionice](https://github.com/maxionice)*
