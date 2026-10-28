#!/usr/bin/env python3
"""
===============================================================================
FolderWatchNArrange - Universal Folder Watcher & Auto-Arranger (macOS/Linux)
Author: lalitaalaalitah
Website: https://www.lalitaalaalitah.com
GitHub: https://github.com/lalitaalaalitah
===============================================================================
"""

import argparse
import datetime
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

__version__ = "1.1.1"
__author__ = "lalitaalaalitah"
__website__ = "https://www.lalitaalaalitah.com"
__github__ = "https://github.com/lalitaalaalitah"

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "folder_watch_n_arrange"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "rules.json"
DEFAULT_HISTORY_FILE = DEFAULT_CONFIG_DIR / "history.json"

# ANSI Colors (Catppuccin Mocha)
CLR_RESET = "\033[0m"
CLR_BLUE = "\033[38;2;137;180;250m"
CLR_GOLD = "\033[38;2;249;226;175m"
CLR_GREEN = "\033[38;2;166;227;161m"
CLR_RED = "\033[38;2;243;139;168m"
CLR_MAUVE = "\033[38;2;203;166;247m"
CLR_TEXT = "\033[38;2;205;214;244m"
CLR_SUBTEXT = "\033[38;2;166;173;200m"


def print_terminal_banner():
    """Print Catppuccin Mocha styled terminal banner with branding metadata."""
    banner = f"""{CLR_BLUE}
 ╔═══════════════════════════════════════════════════════════════════════════╗
 ║ {CLR_GOLD}FolderWatchNArrange v{__version__:<10}{CLR_BLUE}                                    ║
 ║ {CLR_TEXT}Universal Folder Watcher & Auto-Arranger (macOS & Linux)                  {CLR_BLUE}║
 ╠═══════════════════════════════════════════════════════════════════════════╣
 ║ {CLR_SUBTEXT}Author : {CLR_TEXT}{__author__:<58}{CLR_BLUE}║
 ║ {CLR_SUBTEXT}Website: {CLR_TEXT}{__website__:<58}{CLR_BLUE}║
 ║ {CLR_SUBTEXT}GitHub : {CLR_TEXT}{__github__:<58}{CLR_BLUE}║
 ╚═══════════════════════════════════════════════════════════════════════════╝{CLR_RESET}
"""
    print(banner)


def default_rules() -> list[dict]:
    """Default cross-platform rules for SD Card, Camera, Recorders, and Desktop."""
    return [
        {
            "name": "SD Card, Camera & Phone Photos",
            "sources": [
                "/Volumes/*/DCIM/**",
                "/Volumes/*/*.JPG",
                "/Volumes/*/*.CR*",
                "/Volumes/*/*.ARW",
                "/Volumes/*/*.NEF",
                "/media/*/*/DCIM/**",
                "/run/media/*/*/DCIM/**",
            ],
            "extensions": [".jpg", ".jpeg", ".cr2", ".cr3", ".nef", ".arw", ".dng", ".rw2", ".orf", ".heic"],
            "action": "copy",
            "destination": "~/Pictures/Camera/{year}/{year}-{month}-{day}",
            "on_conflict": "rename",
        },
        {
            "name": "SD Card, Camera & Phone Videos",
            "sources": [
                "/Volumes/*/DCIM/**",
                "/Volumes/*/*.MP4",
                "/Volumes/*/*.MOV",
                "/media/*/*/DCIM/**",
                "/run/media/*/*/DCIM/**",
            ],
            "extensions": [".mp4", ".mov", ".mkv", ".avi"],
            "action": "copy",
            "destination": "~/Movies/Camera/{year}/{year}-{month}",
            "on_conflict": "rename",
        },
        {
            "name": "Audio Recorders & Voice Notes",
            "sources": [
                "/Volumes/*/RECORDER/**",
                "/Volumes/*/RECORD/**",
                "/Volumes/*/AUDIO/**",
                "/Volumes/*/*.WAV",
                "/Volumes/*/*.MP3",
                "/media/*/*/RECORDER/**",
                "/run/media/*/*/RECORDER/**",
            ],
            "extensions": [".wav", ".mp3", ".m4a", ".flac", ".aac"],
            "action": "copy",
            "destination": "~/Audio/Recorders/{year}/{year}-{month}",
            "on_conflict": "rename",
        },
        {
            "name": "Tascam Procapture X8",
            "sources": [
                "/Volumes/*/SOUND/**",
                "/media/*/*/SOUND/**",
                "/run/media/*/*/SOUND/**",
            ],
            "extensions": [".wav", ".bin", ".mp4", ".mp3"],
            "action": "copy",
            "destination": "/Volumes/Cablet_WD_2TB_20251206/Music/x8/SOUND/{year}/{year}.{month}/{year}{month}{day}",
            "on_conflict": "rename",
        },
        {
            "name": "Desktop Screenshots",
            "sources": ["~/Desktop"],
            "pattern": r"^(Screen ?Shot|Screenshot)",
            "extensions": [".png", ".jpg", ".jpeg"],
            "action": "move",
            "destination": "~/Pictures/Screenshots/{year}-{month}",
            "on_conflict": "rename",
        },
        {
            "name": "Desktop Downloaded PDFs",
            "sources": ["~/Desktop"],
            "extensions": [".pdf"],
            "action": "move",
            "destination": "~/Documents/PDFs/{year}",
            "on_conflict": "rename",
        },
    ]


class ArrangeEngine:
    def __init__(self, config_path: Path = DEFAULT_CONFIG_FILE, history_path: Path = DEFAULT_HISTORY_FILE):
        self.config_path = config_path
        self.history_path = history_path
        self.history = self._load_history()

    def _load_history(self) -> set[str]:
        if self.history_path.is_file():
            try:
                with open(self.history_path, "r", encoding="utf-8") as f:
                    return set(json.load(f))
            except Exception:
                pass
        return set()

    def _save_history(self):
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        # ponytail: history cap at 50,000 entries; switch to sqlite if tracking millions of files
        if len(self.history) > 50000:
            self.history = set(list(self.history)[-40000:])
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(list(self.history), f, indent=2)

    def load_rules(self) -> list[dict]:
        if not self.config_path.is_file():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            rules = default_rules()
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(rules, f, indent=2)
            print(f"{CLR_GREEN}Created default rules at {self.config_path}{CLR_RESET}")
            return rules
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def resolve_sources(self, source_patterns: list[str]) -> list[Path]:
        """Expand user paths and globs across macOS /Volumes and Linux /media."""
        discovered: set[Path] = set()
        for pattern in source_patterns:
            expanded = os.path.expanduser(pattern)
            if any(ch in expanded for ch in ["*", "?", "["]):
                for match in glob.glob(expanded, recursive=True):
                    p = Path(match)
                    if p.is_file():
                        discovered.add(p)
                    elif p.is_dir():
                        discovered.update(p.rglob("*") if "**" in pattern else p.glob("*"))
            else:
                p = Path(expanded)
                if p.is_file():
                    discovered.add(p)
                elif p.is_dir():
                    discovered.update(p.iterdir())
        return [p for p in discovered if p.is_file()]

    def is_file_stable(self, path: Path, settle_seconds: float = 2.0) -> bool:
        """Check if file is finished copying or being written."""
        # ponytail: mtime + size stability check; avoid polling file locks or lsof
        try:
            st = path.stat()
            now = time.time()
            if (now - st.st_mtime) < settle_seconds:
                return False
            return True
        except (OSError, FileNotFoundError):
            return False

    def build_destination_path(self, src: Path, dest_template: str, st: os.stat_result) -> Path:
        dt = datetime.datetime.fromtimestamp(st.st_mtime)
        expanded = os.path.expanduser(dest_template)
        rendered = expanded.format(
            year=f"{dt.year:04d}",
            month=f"{dt.month:02d}",
            day=f"{dt.day:02d}",
            hour=f"{dt.hour:02d}",
            minute=f"{dt.minute:02d}",
            date=dt.strftime("%Y-%m-%d"),
            ext=src.suffix.lstrip("."),
            stem=src.stem,
            name=src.name,
        )
        dest_dir = Path(rendered)
        return dest_dir / src.name

    def resolve_conflict(self, dest: Path, on_conflict: str) -> Path | None:
        if not dest.exists():
            return dest
        if on_conflict == "overwrite":
            return dest
        if on_conflict == "skip":
            return None
        # on_conflict == 'rename'
        counter = 1
        stem = dest.stem
        suffix = dest.suffix
        parent = dest.parent
        while True:
            candidate = parent / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                return candidate
            counter += 1

    def match_rule(self, path: Path, rule: dict) -> bool:
        if path.name.startswith((".", "._", "Thumbs.db")) or path.suffix.lower() in [".tmp", ".part"]:
            return False

        exts = [e.lower() if e.startswith(".") else f".{e.lower()}" for e in rule.get("extensions", [])]
        if exts and path.suffix.lower() not in exts:
            return False

        pattern = rule.get("pattern")
        if pattern and not re.search(pattern, path.name):
            return False

        min_size = rule.get("min_size_bytes")
        if min_size is not None and path.stat().st_size < min_size:
            return False

        return True

    def process_file(self, path: Path, rule: dict, dry_run: bool = False) -> bool:
        try:
            st = path.stat()
        except (OSError, FileNotFoundError):
            return False

        action = rule.get("action", "copy").lower()
        key = f"{path.resolve()}::{st.st_size}::{int(st.st_mtime)}"

        if action == "copy" and key in self.history:
            return False

        dest = self.build_destination_path(path, rule.get("destination", "~/Arranged"), st)
        final_dest = self.resolve_conflict(dest, rule.get("on_conflict", "rename"))
        if final_dest is None:
            return False

        verb = "WOULD MOVE" if (action == "move" and dry_run) else (
            "WOULD COPY" if dry_run else (
                "MOVING" if action == "move" else "COPYING"
            )
        )
        color = CLR_MAUVE if "MOVE" in verb else CLR_GREEN
        print(f"[{color}{verb}{CLR_RESET}] {path} -> {final_dest}")

        if not dry_run:
            final_dest.parent.mkdir(parents=True, exist_ok=True)
            if action == "move":
                shutil.move(str(path), str(final_dest))
            else:
                shutil.copy2(str(path), str(final_dest))
                self.history.add(key)
                self._save_history()

        return True

    def run_cycle(self, rules: list[dict], dry_run: bool = False) -> int:
        processed_count = 0
        for rule in rules:
            sources = rule.get("sources", [])
            matched_paths = self.resolve_sources(sources)
            for path in matched_paths:
                if not self.match_rule(path, rule):
                    continue
                if not self.is_file_stable(path):
                    continue
                if self.process_file(path, rule, dry_run=dry_run):
                    processed_count += 1
        return processed_count


def get_current_mounts() -> set[str]:
    """Retrieve current mount paths on macOS or Linux."""
    # ponytail: list /Volumes or read /proc/mounts; avoids psutil / pyudev
    mounts = set()
    if sys.platform == "darwin":
        vol_path = Path("/Volumes")
        if vol_path.is_dir():
            try:
                for entry in vol_path.iterdir():
                    if entry.is_dir() and not entry.is_symlink():
                        mounts.add(str(entry.resolve()))
            except OSError:
                pass
    else:
        # Linux
        for candidate in ["/media", "/run/media"]:
            p = Path(candidate)
            if p.is_dir():
                try:
                    for sub in p.rglob("*"):
                        if sub.is_dir() and sub.parent != p:
                            mounts.add(str(sub.resolve()))
                except OSError:
                    pass
        proc_mounts = Path("/proc/mounts")
        if proc_mounts.is_file():
            try:
                for line in proc_mounts.read_text().splitlines():
                    parts = line.split()
                    if len(parts) >= 2 and (parts[1].startswith("/media") or parts[1].startswith("/run/media") or parts[1].startswith("/mnt")):
                        mounts.add(parts[1])
            except OSError:
                pass
    return mounts


def watch_mount_events(engine: ArrangeEngine, dry_run: bool = False, poll_interval: float = 2.0):
    """Event loop kicking off processing as soon as an SD card, HDD, camera, or recorder mounts."""
    print(f"{CLR_BLUE}Listening for storage mounts (SD Cards, Cameras, Phones, Recorders, HDDs)...{CLR_RESET}")
    print(f"{CLR_SUBTEXT}Press Ctrl+C to stop.{CLR_RESET}\n")

    known_mounts = get_current_mounts()
    rules = engine.load_rules()

    # Initial scan of already mounted drives
    engine.run_cycle(rules, dry_run=dry_run)

    try:
        while True:
            time.sleep(poll_interval)
            current_mounts = get_current_mounts()
            new_mounts = current_mounts - known_mounts
            if new_mounts:
                for m in new_mounts:
                    print(f"{CLR_GOLD}⚡ New storage device mounted: {m}{CLR_RESET}")
                time.sleep(1.0)
                rules = engine.load_rules()
                n = engine.run_cycle(rules, dry_run=dry_run)
                print(f"{CLR_GREEN}Processed {n} file(s) from mount.{CLR_RESET}\n")
            known_mounts = current_mounts
    except KeyboardInterrupt:
        print(f"\n{CLR_GOLD}Mount watcher stopped gracefully.{CLR_RESET}")


def install_os_trigger():
    """Install native OS mount watcher (macOS LaunchAgent or Linux systemd user unit)."""
    executable = sys.argv[0]
    real_exe = str(Path(executable).resolve())

    if sys.platform == "darwin":
        plist_path = Path.home() / "Library" / "LaunchAgents" / "com.lalitaalaalitah.folderwatchnarrange.plist"
        plist_path.parent.mkdir(parents=True, exist_ok=True)
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.lalitaalaalitah.folderwatchnarrange</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{real_exe}</string>
        <string>scan</string>
    </array>
    <key>WatchPaths</key>
    <array>
        <string>/Volumes</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
        plist_path.write_text(plist_content, encoding="utf-8")
        subprocess.run(["launchctl", "unload", str(plist_path)], stderr=subprocess.DEVNULL)
        subprocess.run(["launchctl", "load", str(plist_path)])
        print(f"{CLR_GREEN}Installed & activated macOS LaunchAgent at {plist_path}{CLR_RESET}")
        print(f"{CLR_BLUE}Kicks off scan whenever an SD Card, Phone, or HDD is plugged into /Volumes.{CLR_RESET}")
    else:
        # Linux systemd user service + path
        service_dir = Path.home() / ".config" / "systemd" / "user"
        service_dir.mkdir(parents=True, exist_ok=True)
        path_unit = service_dir / "folderwatchnarrange-mount.path"
        service_unit = service_dir / "folderwatchnarrange-mount.service"

        path_unit.write_text(f"""[Unit]
Description=Watch mount directories for SD cards, HDDs, recorders
[Path]
PathModified=/run/media
PathModified=/media
Unit=folderwatchnarrange-mount.service
[Install]
WantedBy=paths.target
""")
        service_unit.write_text(f"""[Unit]
Description=FolderWatchNArrange Scan on Mount
[Service]
ExecStart={sys.executable} {real_exe} scan
Type=oneshot
""")
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
        subprocess.run(["systemctl", "--user", "enable", "--now", "folderwatchnarrange-mount.path"], check=False)
        print(f"{CLR_GREEN}Installed & activated Linux systemd path unit at {path_unit}{CLR_RESET}")


def self_test():
    """Run built-in verification suite."""
    import tempfile
    print(f"{CLR_BLUE}Running built-in tests...{CLR_RESET}")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        cfg_file = tmp / "rules.json"
        hist_file = tmp / "history.json"
        src_dir = tmp / "src"
        dest_dir = tmp / "dest"
        src_dir.mkdir()
        dest_dir.mkdir()

        img = src_dir / "IMG_0001.JPG"
        img.write_text("dummy photo data")
        past = time.time() - 10
        os.utime(img, (past, past))

        rules = [
            {
                "name": "Test Photos",
                "sources": [str(src_dir)],
                "extensions": [".jpg"],
                "action": "copy",
                "destination": str(dest_dir / "{year}"),
                "on_conflict": "rename",
            }
        ]
        with open(cfg_file, "w") as f:
            json.dump(rules, f)

        engine = ArrangeEngine(config_path=cfg_file, history_path=hist_file)
        count = engine.run_cycle(rules, dry_run=False)
        assert count == 1, f"Expected 1 processed file, got {count}"

        year = str(datetime.datetime.now().year)
        expected_dest = dest_dir / year / "IMG_0001.JPG"
        assert expected_dest.is_file(), f"Expected file at {expected_dest}"
        assert img.is_file(), "Source file should remain after copy"

        count2 = engine.run_cycle(rules, dry_run=False)
        assert count2 == 0, f"Expected 0 on re-run, got {count2}"

        doc = src_dir / "audio.wav"
        doc.write_text("audio sample")
        os.utime(doc, (past, past))
        audio_rules = [
            {
                "name": "Test Audio",
                "sources": [str(src_dir)],
                "extensions": [".wav"],
                "action": "copy",
                "destination": str(dest_dir / "Audio"),
                "on_conflict": "rename",
            }
        ]
        count_audio = engine.run_cycle(audio_rules, dry_run=False)
        assert count_audio == 1, f"Expected 1 copied audio file, got {count_audio}"
        assert (dest_dir / "Audio" / "audio.wav").is_file()

        mounts = get_current_mounts()
        assert isinstance(mounts, set)

    print(f"{CLR_GREEN}All self-tests passed successfully!{CLR_RESET}")


def main():
    parser = argparse.ArgumentParser(
        prog="folder-watch-n-arrange",
        description="FolderWatchNArrange - Universal Folder Watcher & Auto-Arranger (macOS & Linux)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_FILE, help="Path to rules.json")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without copying or moving")

    subparsers = parser.add_subparsers(dest="command")

    # watch command
    watch_parser = subparsers.add_parser("watch", help="Continuously watch folders and apply rules")
    watch_parser.add_argument("-i", "--interval", type=float, default=5.0, help="Poll interval in seconds (default: 5.0)")

    # watch-mounts command
    mount_parser = subparsers.add_parser("watch-mounts", help="Watch for newly mounted SD cards, cameras, phones, HDDs, and audio recorders")
    mount_parser.add_argument("-i", "--interval", type=float, default=2.0, help="Mount check interval in seconds (default: 2.0)")

    # install-triggers command
    subparsers.add_parser("install-triggers", help="Install native OS mount trigger (LaunchAgent on macOS, systemd path on Linux)")

    # scan command
    subparsers.add_parser("scan", help="Scan folders once, execute rules, and exit")

    # rules command
    rules_parser = subparsers.add_parser("rules", help="Manage and inspect rules")
    rules_parser.add_argument("--init", action="store_true", help="Initialize or overwrite with default rules")

    # test command
    subparsers.add_parser("test", help="Execute built-in test suite")

    args = parser.parse_args()

    print_terminal_banner()

    if args.command == "test":
        self_test()
        sys.exit(0)

    if args.command == "install-triggers":
        install_os_trigger()
        sys.exit(0)

    engine = ArrangeEngine(config_path=args.config)

    if args.command == "rules":
        if args.init:
            args.config.parent.mkdir(parents=True, exist_ok=True)
            with open(args.config, "w", encoding="utf-8") as f:
                json.dump(default_rules(), f, indent=2)
            print(f"{CLR_GREEN}Initialized default rules at {args.config}{CLR_RESET}")
        else:
            rules = engine.load_rules()
            print(f"{CLR_GOLD}Configured Rules ({args.config}):{CLR_RESET}")
            print(json.dumps(rules, indent=2))
        sys.exit(0)

    if args.command == "scan":
        rules = engine.load_rules()
        print(f"{CLR_BLUE}Running single scan pass (dry_run={args.dry_run})...{CLR_RESET}")
        n = engine.run_cycle(rules, dry_run=args.dry_run)
        print(f"{CLR_GREEN}Scan complete. Processed {n} file(s).{CLR_RESET}")
        sys.exit(0)

    if args.command == "watch-mounts":
        interval = getattr(args, "interval", 2.0)
        watch_mount_events(engine, dry_run=args.dry_run, poll_interval=interval)
        sys.exit(0)

    # Default to watch mode if no subcommand specified or command is watch
    rules = engine.load_rules()
    interval = getattr(args, "interval", 5.0)
    print(f"{CLR_BLUE}Starting watcher loop (interval: {interval}s, dry_run={args.dry_run})...{CLR_RESET}")
    print(f"{CLR_SUBTEXT}Press Ctrl+C to stop.{CLR_RESET}\n")

    try:
        while True:
            engine.run_cycle(rules, dry_run=args.dry_run)
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n{CLR_GOLD}FolderWatchNArrange stopped gracefully.{CLR_RESET}")


if __name__ == "__main__":
    main()
