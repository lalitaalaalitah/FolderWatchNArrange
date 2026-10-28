# FolderWatchNArrange

[![Author](https://img.shields.io/badge/Author-lalitaalaalitah-brightgreen)](https://www.lalitaalaalitah.com)
[![Website](https://img.shields.io/badge/Website-lalitaalaalitah.com-blue)](https://www.lalitaalaalitah.com)
[![GitHub](https://img.shields.io/badge/GitHub-lalitaalaalitah-black)](https://github.com/lalitaalaalitah)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange)](#)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](#)

**FolderWatchNArrange** is a lightweight, universal directory watcher and auto-arranger for **macOS** and **Linux**. It automatically detects files from SD Cards, Cameras, Desktop, Downloads, or any specified folder and copies or moves them according to user-defined routing rules (with dynamic date/extension/name templates and duplicate avoidance).

---

## Key Features

- **Universal macOS & Linux Support**: Seamlessly detects removable volumes (`/Volumes/*` on macOS; `/media/*` or `/run/media/*` on Linux) and local directories (`~/Desktop`, `~/Downloads`).
- **Zero Heavy Dependencies**: Built on Python standard library (`pathlib`, `shutil`, `json`, `time`, `glob`) — runs anywhere with `uv` or Python 3.10+.
- **File Stability & Incomplete Write Guard**: Avoids moving or corrupting partially written files or active camera imports via settling window verification.
- **Dynamic Destination Templating**: Route files using `{year}`, `{month}`, `{day}`, `{hour}`, `{minute}`, `{date}`, `{ext}`, `{stem}`, and `{name}` tokens.
- **Duplicate Prevention & History Tracking**: Automatically remembers copied files in `~/.config/folder_watch_n_arrange/history.json` to avoid redundant transfers.
- **Conflict Resolution**: Configurable conflict handling (`rename`, `skip`, or `overwrite`).
- **Dry-Run Preview**: Preview rule actions safely before applying disk changes.

---

## Installation

Using [`uv`](https://github.com/astral-sh/uv):

```bash
uv pip install -e .
```

Or run directly without installation:

```bash
uv run folder_watch_n_arrange.py --help
```

---

## Quick Usage

### 1. View or Initialize Default Rules
```bash
uv run folder_watch_n_arrange.py rules --init
```

### 2. Single Scan Pass (Preview with Dry-Run)
```bash
uv run folder_watch_n_arrange.py scan --dry-run
```

### 3. Continuous Watch Mode
```bash
uv run folder_watch_n_arrange.py watch --interval 5.0
```

For comprehensive configuration guides, rule schemas, and daemon/service setups, see [HOW_TO_USE.md](HOW_TO_USE.md).

---

## Author & Metadata

- **Author**: lalitaalaalitah
- **Website**: [https://www.lalitaalaalitah.com](https://www.lalitaalaalitah.com)
- **GitHub**: [https://github.com/lalitaalaalitah](https://github.com/lalitaalaalitah)
- **Version**: `1.0.0`
