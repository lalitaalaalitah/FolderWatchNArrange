{ lib, python3Packages }:

python3Packages.buildPythonApplication {
  pname = "folder-watch-n-arrange";
  version = "1.1.0";
  pyproject = true;

  src = ./.;

  build-system = [
    python3Packages.hatchling
  ];

  meta = with lib; {
    description = "Universal Folder Watcher & Auto-Arranger (macOS & Linux)";
    homepage = "https://github.com/lalitaalaalitah/FolderWatchNArrange";
    license = licenses.mit;
    platforms = platforms.unix;
    mainProgram = "folder-watch-n-arrange";
  };
}
