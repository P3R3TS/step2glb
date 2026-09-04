# Build Instructions

## step2glb — STEP/IGES to GLB Converter

---

**Document version:** 1.0  
**Date:** September 2026  
**Applicable standards:** GOST 19.201-78, GOST 19.701-90  

---

## 1. Development Environment Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.8 | 3.11+ |
| pip | 20.0 | latest |
| OS | Windows 7 / Linux / macOS 10.14 | Windows 10+ |
| RAM | 2 GB | 4 GB+ |
| Disk | 200 MB | 500 MB |

---

## 2. Installing Dependencies

### 2.1. Virtual environment (recommended)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 2.2. Install packages

```bash
pip install -r requirements.txt
```

### 2.3. Verify installation

```bash
python -c "import cascadio; print('cascadio', cascadio.__version__)"
python -c "import tkinterdnd2; print('tkinterdnd2 OK')"
```

---

## 3. Running from Source

```bash
python main.py
```

Or as a package:

```bash
python -m src.main
```

---

## 4. Building with PyInstaller

### 4.1. Install PyInstaller

```bash
pip install pyinstaller>=5.0
```

### 4.2. Quick build

```bash
pyinstaller --onefile --windowed --name step2glb main.py
```

### 4.3. Build options

| Option | Description |
|--------|-------------|
| `--onefile` | Single .exe file |
| `--windowed` | No console window |
| `--name step2glb` | Output filename |
| `--icon=icon.ico` | Application icon (optional) |
| `--add-data "step2glb.ini;."` | Bundle INI file (optional) |
| `--onedir` | Directory bundle (portable, faster startup) |

### 4.4. Full build with icon and INI

```bash
pyinstaller --onefile --windowed --name step2glb ^
    --icon=icon.ico ^
    --add-data "step2glb.ini;." ^
    main.py
```

### 4.5. Build via script

```bash
python build/pyinstaller/build_portable.py
```

### 4.6. Output location

```
dist/
  step2glb.exe     # standalone executable (~80-100 MB)
```

---

## 5. Building an Installer (Inno Setup)

### 5.1. Prerequisites

- [Inno Setup 6+](https://jrsoftware.org/isinfo.php)
- `dist/step2glb.exe` (built with PyInstaller)

### 5.2. Basic installer

```bash
cd build/inno_setup
iscc installer.iss
```

### 5.3. Installer with custom questions

```bash
iscc installer_questions.iss
```

This version adds user prompts for:
- Installation directory
- Desktop shortcut creation
- Start menu folder
- File associations (.stp, .step, .igs, .iges)

### 5.4. Output

```
installer/
  step2glb-setup-x.x.x.exe     # Windows installer
```

---

## 6. Platform-Specific Build Scripts

### 6.1. Windows (portable)

```bash
python build/build_all.py --platform windows --mode portable
```

Or directly:

```bat
build\build_windows.bat portable
```

### 6.2. Windows (installer)

```bash
python build/build_all.py --platform windows --mode installer
```

Or directly:

```bat
build\build_windows.bat installer
```

### 6.3. Linux

```bash
python build/build_all.py --platform linux
```

Or directly:

```bash
chmod +x build/build_linux.sh
./build/build_linux.sh
```

### 6.4. macOS

```bash
python build/build_all.py --platform macos
```

Or directly:

```bash
chmod +x build/build_macos.sh
./build/build_macos.sh
```

### 6.5. All platforms

```bash
python build/build_all.py --all
```

---

## 7. Build Output

| Platform | Mode | Output | Size |
|----------|------|--------|------|
| Windows | Portable | `dist/step2glb.exe` | ~80-100 MB |
| Windows | Installer | `installer/step2glb-setup.exe` | ~80-100 MB |
| Windows | Directory | `dist/step2glb/` | ~150 MB |
| Linux | AppImage | `dist/step2glb.AppImage` | ~80-100 MB |
| Linux | Directory | `dist/step2glb/` | ~150 MB |
| macOS | App bundle | `dist/step2glb.app` | ~80-100 MB |
| macOS | DMG | `dist/step2glb.dmg` | ~80-100 MB |

---

## 8. Testing

### 8.1. Module import test

```bash
python -c "from src.config import PRESETS; print(PRESETS)"
python -c "from src.utils import has_non_ascii; print(has_non_ascii('test'))"
```

### 8.2. GUI test

```bash
python main.py
```

### 8.3. Built executable test

1. Run `dist/step2glb.exe`.
2. Select a test STEP/IGES file.
3. Click "Convert".
4. Verify the `.glb` file is created.

---

## 9. Debugging

### 9.1. Console output

Run from console for debug output (the `--windowed` .exe suppresses this):

```bash
python main.py
```

### 9.2. Inspecting PyInstaller archives

```bash
pyi-archive_viewer dist/step2glb.exe
```

---

## 10. Security Notes

- No network communication — all operations are local.
- Temporary files are cleaned on exit.
- Code contains no secrets, keys, or tokens.
