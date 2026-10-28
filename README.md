# FolderWatchNArrange

[![Author](https://img.shields.io/badge/Author-lalitaalaalitah-brightgreen)](https://www.lalitaalaalitah.com)
[![Website](https://img.shields.io/badge/Website-lalitaalaalitah.com-blue)](https://www.lalitaalaalitah.com)
[![GitHub](https://img.shields.io/badge/GitHub-lalitaalaalitah-black)](https://github.com/lalitaalaalitah)
[![Version](https://img.shields.io/badge/Version-1.1.1-orange)](#)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](#)

**FolderWatchNArrange** is a lightweight, universal directory watcher and auto-arranger for **macOS** and **Linux**. It automatically detects storage mount events (SD Cards, Cameras, Phones, Voice Recorders, external HDDs) or local directories (Desktop, Downloads) and copies or moves files into organized date- and type-structured folders.

---

## Key Features

- **Storage Mount Auto-Kickoff**: Automatically kicks off processing whenever an SD Card, Camera, Phone, Voice Recorder (Zoom, Tascam, Sony), or USB HDD is mounted (`/Volumes` on macOS; `/media` or `/run/media` on Linux).
- **Nix Flake & Home Manager Ready**: Fully nixified with cross-platform flake support (`aarch64-darwin`, `x86_64-darwin`, `aarch64-linux`, `x86_64-linux`) and a ready-to-use Home Manager module.
- **Native OS Triggers**: One-command installation of macOS `LaunchAgent` (`WatchPaths = ["/Volumes"]`) or Linux `systemd.path` unit to run on mount with zero background idle resource consumption.
- **Zero Heavy Dependencies**: 100% Python standard library (`pathlib`, `shutil`, `json`, `glob`, `os`).
- **Incomplete Write & Settle Protection**: Automatically verifies file stability before processing to ensure active camera imports or card copies are not moved prematurely.
- **Dynamic Routing & Deduplication**: Template target folders with `{year}`, `{month}`, `{day}`, `{date}`, `{stem}`, `{ext}` and track copied files to prevent duplicate copies.

---

## Installation & Execution

### With Nix Flakes

Run directly without installing:
```bash
nix run github:lalitaalaalitah/FolderWatchNArrange -- --help
```

Or build locally:
```bash
nix build
./result/bin/folder-watch-n-arrange --version
```

### With `uv` or Python 3.10+

```bash
uv run folder_watch_n_arrange.py --help
```

---

## Quick Usage

### 1. Auto-Kick on Mount
To listen for new SD cards, HDDs, phones, and audio recorders in the foreground:
```bash
# Nix
nix run . -- watch-mounts

# uv
uv run folder_watch_n_arrange.py watch-mounts
```

### 2. Install Native OS Mount Trigger (Runs in background on mount)
```bash
# macOS installs ~/Library/LaunchAgents/com.lalitaalaalitah.folderwatchnarrange.plist
# Linux installs ~/.config/systemd/user/folderwatchnarrange-mount.path
uv run folder_watch_n_arrange.py install-triggers
```

### 3. Dry-Run Scan Pass
```bash
uv run folder_watch_n_arrange.py scan --dry-run
```

For full details, rule schema, and Home Manager configuration, see [HOW_TO_USE.md](HOW_TO_USE.md).

---

## Author & Metadata

- **Author**: lalitaalaalitah
- **Website**: [https://www.lalitaalaalitah.com](https://www.lalitaalaalitah.com)
- **GitHub**: [https://github.com/lalitaalaalitah](https://github.com/lalitaalaalitah)
- **Version**: `1.1.1`
