# HOW TO USE: FolderWatchNArrange

**FolderWatchNArrange** is a cross-platform tool for macOS and Linux that monitors directories and storage mount events (SD cards, digital cameras, external HDDs, phones, and voice recorders), routing files according to configurable JSON rules.

---

## 1. Nix Integration

### Running via Nix Flakes
```bash
# Run latest directly from GitHub
nix run github:lalitaalaalitah/FolderWatchNArrange -- --version

# Run locally
nix run . -- --help

# Enter development shell
nix develop
```

### Home Manager Module
Add FolderWatchNArrange to your Home Manager flake:

```nix
{
  inputs = {
    folder-watch-n-arrange.url = "github:lalitaalaalitah/FolderWatchNArrange";
  };

  outputs = { self, nixpkgs, folder-watch-n-arrange, ... }: {
    # In your home-manager configuration:
    homeManagerConfigurations."user" = home-manager.lib.homeManagerConfiguration {
      modules = [
        folder-watch-n-arrange.homeManagerModules.default
        {
          services.folder-watch-n-arrange = {
            enable = true;
            onMountOnly = true; # Triggers on SD card / HDD mount via LaunchAgent (macOS) or systemd.path (Linux)
          };
        }
      ];
    };
  };
}
```

---

## 2. CLI Commands Overview

| Command | Description |
|---|---|
| `folder-watch-n-arrange watch-mounts` | Foreground event loop detecting newly mounted SD cards, cameras, phones, and audio recorders |
| `folder-watch-n-arrange install-triggers` | Installs native OS mount trigger (LaunchAgent on macOS, systemd.path on Linux) |
| `folder-watch-n-arrange watch` | Continuous polling watcher loop across specified directories |
| `folder-watch-n-arrange scan` | Scan all sources once and process immediately |
| `folder-watch-n-arrange scan --dry-run` | Preview actions without copying or moving any files |
| `folder-watch-n-arrange rules` | View currently loaded JSON rules |
| `folder-watch-n-arrange rules --init` | Reinitialize or create default rules file |
| `folder-watch-n-arrange test` | Run built-in self-test verification |
| `folder-watch-n-arrange --version` | Display version (`1.1.0`) |

---

## 3. Storage Mount Kickoff Mechanisms

FolderWatchNArrange supports two kickoff models:

### Option A: Native OS Event Trigger (0 Idle CPU)
Run:
```bash
folder-watch-n-arrange install-triggers
```
- **macOS**: Configures a `LaunchAgent` monitoring `/Volumes`. As soon as an SD card, camera, phone, or HDD mounts in `/Volumes`, macOS triggers `folder-watch-n-arrange scan`.
- **Linux**: Configures a `systemd.path` unit monitoring `/media` and `/run/media`. As soon as a device mounts, systemd triggers the oneshot service.

### Option B: Standalone Foreground Mount Watcher
```bash
folder-watch-n-arrange watch-mounts --interval 2.0
```
Diffs active mounts and executes a scan the moment a new storage partition appears.

---

## 4. Configuration & Rule Schema

Rules reside at `~/.config/folder_watch_n_arrange/rules.json`:

```json
[
  {
    "name": "SD Card, Camera & Phone Photos",
    "sources": [
      "/Volumes/*/DCIM/**",
      "/media/*/*/DCIM/**",
      "/run/media/*/*/DCIM/**"
    ],
    "extensions": [".jpg", ".jpeg", ".cr2", ".cr3", ".nef", ".arw", ".dng", ".heic"],
    "action": "copy",
    "destination": "~/Pictures/Camera/{year}/{year}-{month}-{day}",
    "on_conflict": "rename"
  },
  {
    "name": "Audio Recorders & Voice Notes",
    "sources": [
      "/Volumes/*/RECORDER/**",
      "/Volumes/*/RECORD/**",
      "/Volumes/*/AUDIO/**",
      "/Volumes/*/*.WAV",
      "/media/*/*/RECORDER/**"
    ],
    "extensions": [".wav", ".mp3", ".m4a", ".flac", ".aac"],
    "action": "copy",
    "destination": "~/Audio/Recorders/{year}/{year}-{month}",
    "on_conflict": "rename"
  },
  {
    "name": "Desktop Clean PDFs",
    "sources": ["~/Desktop"],
    "extensions": [".pdf"],
    "action": "move",
    "destination": "~/Documents/PDFs/{year}",
    "on_conflict": "rename"
  }
]
```

### Destination Tokens
- `{year}`: 4-digit year (`2026`)
- `{month}`: 2-digit month (`10`)
- `{day}`: 2-digit day (`28`)
- `{hour}`: 2-digit hour (`21`)
- `{minute}`: 2-digit minute (`45`)
- `{date}`: ISO date string (`2026-10-28`)
- `{ext}`: Extension without leading period (`jpg`)
- `{stem}`: Filename without extension (`IMG_0001`)
- `{name}`: Complete filename (`IMG_0001.JPG`)

---

## 5. Author & Metadata

- **Author**: lalitaalaalitah
- **Website**: https://www.lalitaalaalitah.com
- **GitHub**: https://github.com/lalitaalaalitah
- **Version**: 1.1.0
