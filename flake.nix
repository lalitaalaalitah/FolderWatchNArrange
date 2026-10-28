{
  description = "FolderWatchNArrange - Universal Folder Watcher & Auto-Arranger (macOS & Linux)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        package = pkgs.callPackage ./default.nix {};
      in
      {
        packages = {
          default = package;
          folder-watch-n-arrange = package;
        };

        apps = {
          default = flake-utils.lib.mkApp {
            drv = package;
            exePath = "/bin/folder-watch-n-arrange";
          };
        };

        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.python3
            pkgs.uv
          ];
        };
      }
    ) // {
      homeManagerModules.default = { config, lib, pkgs, ... }:
        let
          cfg = config.services.folder-watch-n-arrange;
          pkg = self.packages.${pkgs.stdenv.hostPlatform.system}.default;
        in
        {
          options.services.folder-watch-n-arrange = {
            enable = lib.mkEnableOption "FolderWatchNArrange background mount triggers and watcher";
            onMountOnly = lib.mkOption {
              type = lib.types.bool;
              default = true;
              description = "Trigger scan on mount events (SD card, camera, HDD, recorder) instead of polling continuously.";
            };
            interval = lib.mkOption {
              type = lib.types.float;
              default = 5.0;
              description = "Polling interval in seconds when onMountOnly is false.";
            };
          };

          config = lib.mkIf cfg.enable (
            lib.mkMerge [
              {
                home.packages = [ pkg ];
              }

              # macOS LaunchAgent
              (lib.mkIf pkgs.stdenv.hostPlatform.isDarwin {
                launchd.agents.folder-watch-n-arrange = {
                  enable = true;
                  config = {
                    ProgramArguments = [
                      "${pkg}/bin/folder-watch-n-arrange"
                    ] ++ (if cfg.onMountOnly then [ "scan" ] else [ "watch" "--interval" (toString cfg.interval) ]);
                    RunAtLoad = true;
                    KeepAlive = !cfg.onMountOnly;
                    WatchPaths = lib.mkIf cfg.onMountOnly [ "/Volumes" ];
                  };
                };
              })

              # Linux systemd
              (lib.mkIf pkgs.stdenv.hostPlatform.isLinux (
                if cfg.onMountOnly then {
                  systemd.user.paths.folder-watch-n-arrange = {
                    Unit = { Description = "Watch mount directories for SD cards, HDDs, recorders"; };
                    Path = {
                      PathModified = [ "/run/media" "/media" ];
                      Unit = "folder-watch-n-arrange.service";
                    };
                    Install = { WantedBy = [ "paths.target" ]; };
                  };
                  systemd.user.services.folder-watch-n-arrange = {
                    Unit = { Description = "FolderWatchNArrange Scan on Mount"; };
                    Service = {
                      ExecStart = "${pkg}/bin/folder-watch-n-arrange scan";
                      Type = "oneshot";
                    };
                  };
                } else {
                  systemd.user.services.folder-watch-n-arrange = {
                    Unit = { Description = "FolderWatchNArrange Daemon"; };
                    Service = {
                      ExecStart = "${pkg}/bin/folder-watch-n-arrange watch --interval ${toString cfg.interval}";
                      Restart = "always";
                    };
                    Install = { WantedBy = [ "default.target" ]; };
                  };
                }
              ))
            ]
          );
        };
    };
}

