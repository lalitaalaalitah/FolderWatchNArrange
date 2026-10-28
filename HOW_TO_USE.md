# HOW TO USE: FolderWatchNArrange

**FolderWatchNArrange** monitors directories on macOS and Linux, matching files against configurable rules to copy or move them to organized target locations.

---

## 1. Commands Overview

The CLI provides intuitive subcommands:

| Command | Description |
|---|---|
| `uv run folder_watch_n_arrange.py watch` | Run continuous watcher loop (polls every N seconds) |
| `uv run folder_watch_n_arrange.py scan` | Run a single scan pass across all sources and exit |
| `uv run folder_watch_n_arrange.py rules` | Display currently loaded rules in JSON |
| `uv run folder_watch_n_arrange.py rules --init` | Generate default rules configuration file |
| `uv run folder_watch_n_arrange.py test` | Run internal verification self-test |
| `uv run folder_watch_n_arrange.py --version` | Display program version (`1.0.0`) |
| `uv run folder_watch_n_arrange.py --dry-run` | Preview actions without modifying any files |

---

## 2. Configuration & Rules

Configuration resides at:
- `~/.config/folder_watch_n_arrange/rules.json` (or custom path via `--config <path>`)

### Rule Schema

Each rule is a JSON object with the following fields:

```json
{
  "name": "Human-readable label for rule",
  "sources": [
    "/Volumes/*/DCIM/**",
    "~/Desktop",
    "/media/*/*/DCIM/**"
  ],
  "extensions": [".jpg", ".jpeg", ".cr2", ".cr3", ".nef", ".arw", ".mp4"],
  "pattern": "^DSC_",
  "min_size_bytes": 1024,
  "action": "copy",
  "destination": "~/Pictures/Camera/{year}/{year}-{month}-{day}",
  "on_conflict": "rename"
}
```

### Explanation of Fields

- **`sources`**: List of directories or glob patterns.
  - macOS Removable Media: `/Volumes/*/DCIM/**`
  - Linux Removable Media: `/media/*/*/DCIM/**` or `/run/media/*/*/DCIM/**`
  - Local Directories: `~/Desktop`, `~/Downloads`
- **`extensions`**: List of file extensions to match (case-insensitive: `.jpg` matches `.JPG`).
- **`pattern`** *(optional)*: Regular expression to match against the filename.
- **`min_size_bytes`** *(optional)*: Minimum file size in bytes to ignore 0-byte or corrupted fragments.
- **`action`**: Either `"copy"` or `"move"`.
  - `"copy"`: Copies the file and records it in `history.json` so it will not be re-copied.
  - `"move"`: Moves the file into the destination hierarchy.
- **`destination`**: Destination directory template. Supported placeholders:
  - `{year}`: 4-digit year (`2026`)
  - `{month}`: 2-digit month (`10`)
  - `{day}`: 2-digit day (`28`)
  - `{hour}`: 2-digit hour (`21`)
  - `{minute}`: 2-digit minute (`30`)
  - `{date}`: ISO date string (`2026-10-28`)
  - `{ext}`: File extension without dot (`jpg`)
  - `{stem}`: File name without extension (`IMG_0001`)
  - `{name}`: Full file name (`IMG_0001.JPG`)
- **`on_conflict`**:
  - `"rename"`: Appends `_1`, `_2`, etc. if target file already exists.
  - `"skip"`: Leaves destination untouched and skips.
  - `"overwrite"`: Overwrites existing target file.

---

## 3. Running as a Background Daemon

### On macOS (LaunchAgent)

Create `~/Library/LaunchAgents/com.lalitaalaalitah.folderwatchnarrange.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.lalitaalaalitah.folderwatchnarrange</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/env</string>
        <string>uv</string>
        <string>run</string>
        <string>/path/to/FolderWatchNArrange/folder_watch_n_arrange.py</string>
        <string>watch</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load with:
```bash
launchctl load ~/Library/LaunchAgents/com.lalitaalaalitah.folderwatchnarrange.plist
```

### On Linux (systemd User Service)

Create `~/.config/systemd/user/folderwatchnarrange.service`:

```ini
[Unit]
Description=FolderWatchNArrange Auto Arranger
After=default.target

[Service]
ExecStart=/usr/bin/env uv run /path/to/FolderWatchNArrange/folder_watch_n_arrange.py watch
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

Enable and start with:
```bash
systemctl --user enable --now folderwatchnarrange.service
```

---

## 4. Metadata

- **Author**: lalitaalaalitah
- **Website**: https://www.lalitaalaalitah.com
- **GitHub**: https://github.com/lalitaalaalitah
- **Version**: 1.0.0
