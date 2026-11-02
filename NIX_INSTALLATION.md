# Nix & Home Manager Installation Guide

[![Author](https://img.shields.io/badge/Author-lalitaalaalitah-brightgreen)](https://www.lalitaalaalitah.com)
[![Website](https://img.shields.io/badge/Website-lalitaalaalitah.com-blue)](https://www.lalitaalaalitah.com)
[![GitHub](https://img.shields.io/badge/GitHub-lalitaalaalitah-black)](https://github.com/lalitaalaalitah)
[![Version](https://img.shields.io/badge/Version-2.0.0-orange)](#)

This guide explains how to add **FolderWatchNArrange** as a Nix flake input and configure it declaratively using **Nix**, **Nix-Darwin**, and **Home Manager**.

---

## 1. Quick Ad-Hoc Execution

To run `FolderWatchNArrange` directly without installing:

```bash
# Display help
nix run github:lalitaalaalitah/FolderWatchNArrange -- --help

# Preview a scan without moving files (dry run)
nix run github:lalitaalaalitah/FolderWatchNArrange -- --dry-run

# Run mount watcher
nix run github:lalitaalaalitah/FolderWatchNArrange -- watch-mounts
```

---

## 2. Adding as a Flake Input

In your system or home flake (`flake.nix`), declare `FolderWatchNArrange` in `inputs`:

```nix
{
  description = "System & User Configuration Flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    
    # Declare FolderWatchNArrange input
    FolderWatchNArrange = {
      url = "github:lalitaalaalitah/FolderWatchNArrange";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, FolderWatchNArrange, ... }@inputs: {
    # Darwin configuration example
    darwinConfigurations."macbook" = nix-darwin.lib.darwinSystem {
      system = "aarch64-darwin";
      specialArgs = inputs; # Passes FolderWatchNArrange to all modules
      modules = [
        ./systems/darwin
        home-manager.darwinModules.home-manager {
          home-manager.extraSpecialArgs = inputs; # Passes to Home Manager modules
          home-manager.users."username" = import ./modules/darwin/home-manager;
        }
      ];
    };

    # NixOS configuration example
    nixosConfigurations."workstation" = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      specialArgs = inputs;
      modules = [
        ./systems/linux
        home-manager.nixosModules.home-manager {
          home-manager.extraSpecialArgs = inputs;
          home-manager.users."username" = import ./modules/common/home-manager;
        }
      ];
    };
  };
}
```

---

## 3. Declarative Home Manager Module

You can configure `FolderWatchNArrange` completely declaratively, managing the package, JSON routing rules, native mount triggers (`LaunchAgent` or `systemd.path`), and shell helpers in a dedicated module (e.g. `custom_apps/common/folder_watch_n_arrange.nix`):

```nix
{ config, lib, pkgs, FolderWatchNArrange, ... }:

let
  cfg = config.programs.folder_watch_n_arrange;
  folderWatchPkg = FolderWatchNArrange.packages.${pkgs.stdenv.hostPlatform.system}.default;
in
{
  options.programs.folder_watch_n_arrange = {
    enable = lib.mkOption {
      type = lib.types.bool;
      default = true;
      description = "Enable FolderWatchNArrange universal folder watcher and auto-arranger";
    };

    kickOnMount = lib.mkOption {
      type = lib.types.bool;
      default = true;
      description = "Automatically trigger processing when an SD Card, Camera, Phone, Voice Recorder, or HDD is mounted.";
    };

    rules = lib.mkOption {
      type = lib.types.listOf lib.types.attrs;
      default = [
        {
          name = "SD Card & Camera Photos";
          sources = [
            "/Volumes/*/DCIM/**"
            "/media/*/*/DCIM/**"
            "/run/media/*/*/DCIM/**"
          ];
          extensions = [ ".jpg", ".jpeg", ".cr2", ".cr3", ".arw", ".dng" ];
          action = "copy";
          destination = "~/Pictures/Camera/{year}/{year}-{month}-{day}";
          on_conflict = "rename";
        }
        {
          name = "Tascam / Voice Recorder Audio";
          sources = [ "/Volumes/*/SOUND/**" ];
          extensions = [ ".wav", ".mp3", ".flac" ];
          action = "copy";
          destination = "~/Audio/Recorders/{year}/{year}.{month}/{year}{month}{day}";
          # Optional post-processing script:
          post_command = "echo 'Transferred {source} to {destination}'";
          on_conflict = "rename";
        }
      ];
      description = "Declarative routing rules for FolderWatchNArrange managed by Nix.";
    };
  };

  config = lib.mkIf cfg.enable {
    # 1. Install package to user profile
    home.packages = [
      folderWatchPkg
    ];

    # 2. Generate declarative rules.json in ~/.config/folder_watch_n_arrange/rules.json
    xdg.configFile."folder_watch_n_arrange/rules.json".text = builtins.toJSON cfg.rules;

    # 3. macOS LaunchAgent: Trigger scan on /Volumes mount (0 idle RAM)
    launchd.agents.folder-watch-n-arrange =
      lib.mkIf (pkgs.stdenv.hostPlatform.isDarwin && cfg.kickOnMount) {
        enable = true;
        config = {
          ProgramArguments = [
            "${folderWatchPkg}/bin/folder-watch-n-arrange"
            "scan"
          ];
          WatchPaths = [ "/Volumes" ];
          RunAtLoad = true;
        };
      };

    # 4. Linux systemd.path: Trigger scan on /media or /run/media mount (0 idle RAM)
    systemd.user.paths.folder-watch-n-arrange =
      lib.mkIf (pkgs.stdenv.hostPlatform.isLinux && cfg.kickOnMount) {
        Unit.Description = "Watch mount directories for storage devices";
        Path = {
          PathModified = [ "/run/media" "/media" ];
          Unit = "folder-watch-n-arrange.service";
        };
        Install.WantedBy = [ "paths.target" ];
      };

    systemd.user.services.folder-watch-n-arrange =
      lib.mkIf (pkgs.stdenv.hostPlatform.isLinux && cfg.kickOnMount) {
        Unit.Description = "FolderWatchNArrange Scan on Mount";
        Service = {
          ExecStart = "${folderWatchPkg}/bin/folder-watch-n-arrange scan";
          Type = "oneshot";
        };
      };

    # 5. Fish Shell integration (optional)
    programs.fish.functions.fwa = {
      body = "${folderWatchPkg}/bin/folder-watch-n-arrange $argv";
      description = "FolderWatchNArrange CLI alias";
    };
  };
}
```

---

## 4. Simple Direct Package Installation

If you only want the CLI binary without configuring the Home Manager module:

```nix
{ pkgs, FolderWatchNArrange, ... }:

{
  home.packages = [
    FolderWatchNArrange.packages.${pkgs.stdenv.hostPlatform.system}.default
  ];
}
```

---

## 5. Locking and Updating

Whenever new versions or features are pushed to GitHub:

```bash
# Update flake lock for this repository
nix flake update FolderWatchNArrange

# Apply changes to your system
just switch
# or
darwin-rebuild switch --flake .
# or
home-manager switch --flake .
```

---

## 6. Verification

Check that the CLI is correctly installed and accessible on your PATH:

```bash
which folder-watch-n-arrange
folder-watch-n-arrange --version
folder-watch-n-arrange rules
```
