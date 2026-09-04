<p align="center">
  <b>step2glb</b><br>
  STEP / IGES to GLB Converter
</p>

<p align="center">
  <a href="docs/ru/USER_MANUAL.md">Русский</a> |
  <b>English</b>
</p>

---

## Overview

**step2glb** is a desktop application that converts 3D CAD files from **STEP** (`.stp`, `.step`) and **IGES** (`.igs`, `.iges`) formats into **GLB** (glTF Binary) — the compact binary format widely used in web apps, game engines, and 3D viewers.

- Drag-and-drop file support (via `tkinterdnd2`)
- Configurable tessellation quality (4 presets + manual control)
- Parallel mesh generation on all CPU cores
- Optional gzip compression (`.glb.gz`)
- Automatic memory management for large files (>500 MB)
- Works on Windows, Linux, and macOS

---

## Download

Prebuilt binaries for all platforms are available on the [Releases](../../releases) page.

| Platform | File | Description |
|----------|------|-------------|
| Windows  | `step2glb-*-windows-portable.zip` | Portable exe + launcher |
| Windows  | `step2glb-setup-*.exe` | Installer with wizard |
| Linux    | `step2glb-*-linux-portable.tar.gz` | Standalone binary |
| macOS    | `step2glb-*-macos-portable.zip` | Standalone binary |

---

## Quick Start

### Option A — Run the prebuilt executable

1. Download the archive for your platform from [Releases](../../releases).
2. Extract and run.

### Option B — Run from source

```bash
git clone https://github.com/yourname/step2glb.git
cd step2glb
pip install -r requirements.txt
python main.py
```

### Option C — Build the executable yourself

```bash
# Install build tools
pip install pyinstaller

# Quick build (current platform)
python build/build_all.py

# Or platform-specific
python build/build_all.py --platform windows
python build/build_all.py --platform linux
python build/build_all.py --platform macos
```

---

## Tessellation Presets

| Preset | Linear Defl. | Angular Defl. | Use case |
|--------|:------------:|:-------------:|----------|
| `draft` | 1.0 | 1.0 | Quick preview |
| `normal` | 0.1 | 0.5 | Balanced (default) |
| `high` | 0.01 | 0.2 | Detailed output |
| `ultra` | 0.001 | 0.1 | Maximum quality |

---

## Supported Formats

| Input | Extensions | Standard |
|-------|------------|----------|
| STEP  | `.stp`, `.step` | ISO 10303 |
| IGES  | `.igs`, `.iges` | ASME Y14.26M |

| Output | Extension | Description |
|--------|-----------|-------------|
| GLB    | `.glb`    | glTF Binary |
| GLB.GZ | `.glb.gz` | gzip-compressed GLB |

---

## Documentation

### By language

| Language | User Manual | Technical Docs | Build Instructions |
|----------|-------------|----------------|-------------------|
| English  | [User Manual](docs/en/USER_MANUAL.md) | [Technical Description](docs/en/TECHNICAL_DESCRIPTION.md) | [Build Instructions](docs/en/BUILD_INSTRUCTIONS.md) |
| Русский  | [Руководство](docs/ru/USER_MANUAL.md) | [Техническое описание](docs/ru/TECHNICAL_DESCRIPTION.md) | [Инструкция по сборке](docs/ru/BUILD_INSTRUCTIONS.md) |

---

## Build System

Build scripts are in the `build/` directory. The build is orchestrated by `build_all.py` which reads configuration from `build_config.json`.

| Script | Platform | Description |
|--------|----------|-------------|
| `build_all.py` | All | Universal build orchestrator |
| `build_windows.bat` | Windows | Portable exe + installer |
| `build_linux.sh` | Linux | Portable binary |
| `build_macos.sh` | macOS | Portable binary |

### Quick build commands

```bash
# Current platform (portable + installer on Windows)
python build/build_all.py

# Specific platform
python build/build_all.py --platform windows
python build/build_all.py --platform linux
python build/build_all.py --platform macos

# Portable only (skip installer)
python build/build_all.py --mode portable

# Clean build artifacts
python build/build_all.py --mode clean
```

---

## Project Structure

```
step2glb/
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT License
├── README.md                  # This file
├── src/
│   ├── __init__.py            # Package metadata
│   ├── config.py              # Constants, presets, defaults
│   ├── utils.py               # Session management, settings I/O
│   ├── worker.py              # Background conversion process
│   ├── widgets.py             # Custom GUI widgets (Tooltip)
│   ├── app.py                 # Main application window
│   └── main.py                # Package entry point
├── build/
│   ├── build_config.json      # Centralized build configuration
│   ├── build_all.py           # Universal build orchestrator
│   ├── build_windows.bat      # Windows build script
│   ├── build_linux.sh         # Linux build script
│   ├── build_macos.sh         # macOS build script
│   ├── pyinstaller/
│   │   ├── build_portable.py  # PyInstaller build wrapper
│   │   └── step2glb.spec      # PyInstaller spec file
│   └── inno_setup/
│       ├── build_config.iss   # Inno Setup shared config
│       ├── installer.iss      # Basic installer
│       └── installer_questions.iss  # Installer with wizard
├── .github/
│   └── workflows/
│       └── build.yml          # CI/CD: auto-build on push/tag
└── docs/
    ├── en/                    # English documentation
    └── ru/                    # Russian documentation
```

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Windows 7 / Linux / macOS 10.14 | Windows 10+ |
| Python | 3.8 | 3.11+ |
| RAM | 2 GB | 4 GB+ |
| Disk | 200 MB | 500 MB |

---

## Dependencies

| Package | Purpose | Required |
|---------|---------|:--------:|
| [cascadio](https://pypi.org/project/cascadio/) | STEP/IGES parsing & tessellation (OpenCASCADE wrapper) | Yes |
| [tkinterdnd2](https://pypi.org/project/tkinterdnd2/) | Drag-and-drop support in the GUI | No |
| [PyInstaller](https://pyinstaller.org/) | Building standalone executables | Build only |
| [Inno Setup](https://jrsoftware.org/isinfo.php) | Windows installer (optional) | Build only |

---

## CI/CD

This project uses GitHub Actions to automatically build binaries for all platforms on every push and release. See [`.github/workflows/build.yml`](.github/workflows/build.yml).

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Commit your changes.
4. Push to the branch: `git push origin feature/my-feature`.
5. Open a Pull Request.

Please follow the existing code style and add docstrings (bilingual: Russian + English).

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## Acknowledgements

- [cascadio](https://pypi.org/project/cascadio/) — Python bindings for OpenCASCADE
- [glTF / GLB](https://www.khronos.org/gltf/) — by Khronos Group
- [OpenCASCADE](https://www.opencascade.com/) — open-source CAD kernel
