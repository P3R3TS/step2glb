#!/usr/bin/env python3
"""Универсальный скрипт сборки step2glb под все основные ОС.

Universal build script for step2glb targeting all major platforms.

Конфигурация: build/build_config.json
Configuration: build/build_config.json

Использование / Usage:
    python build/build_all.py --all                      # Текущая платформа
    python build/build_all.py --platform windows          # Только Windows
    python build/build_all.py --platform linux            # Только Linux
    python build/build_all.py --platform macos            # Только macOS
    python build/build_all.py --platform windows --mode installer  # Windows + установщик
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from _config_loader import load_build_config, get_icon_path, get_project_root

# ---------------------------------------------------------------------------
# Конфигурация из build_config.json / Configuration from build_config.json
# ---------------------------------------------------------------------------

_cfg = load_build_config()

PROJECT_ROOT = get_project_root()
DIST_DIR = PROJECT_ROOT / "dist"
INSTALLER_DIR = PROJECT_ROOT / "installer"
BUILD_DIR = PROJECT_ROOT / "build"

APP_NAME = _cfg["app_name"]
ENTRY_POINT = _cfg["entry_point"]
INI_FILE = PROJECT_ROOT / _cfg["ini_file"]


# ---------------------------------------------------------------------------
# Утилиты / Utilities
# ---------------------------------------------------------------------------

def log(msg: str) -> None:
    """Вывод сообщения с префиксом / Print prefixed message."""
    print(f"[build_all] {msg}")


def run(cmd: list, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    """Запуск команды / Run a command."""
    log(f"Running: {' '.join(str(c) for c in cmd)}")
    return subprocess.run(
        [str(c) for c in cmd],
        cwd=str(cwd or PROJECT_ROOT),
        check=check,
    )


def ensure_venv() -> Path:
    """Создаёт venv, если нет. Возвращает путь к python.

    Create venv if missing. Return path to python.
    """
    venv_dir = PROJECT_ROOT / ".venv"
    if not venv_dir.exists():
        log("Creating virtual environment...")
        run([sys.executable, "-m", "venv", str(venv_dir)])

    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def install_deps(python: Path) -> None:
    """Установка зависимостей / Install dependencies."""
    req_file = PROJECT_ROOT / "requirements.txt"
    if req_file.exists():
        log("Installing dependencies...")
        run([python, "-m", "pip", "install", "-r", str(req_file), "-q"])

    log("Installing PyInstaller...")
    run([python, "-m", "pip", "install", "pyinstaller>=5.0", "-q"])


def clean_dirs(*dirs: Path) -> None:
    """Очистка директорий / Clean directories."""
    for d in dirs:
        if d.exists():
            log(f"Cleaning {d.name}/")
            shutil.rmtree(d, ignore_errors=True)


def _build_pyinstaller_cmd(python: Path, extra: list | None = None) -> list:
    """Формирует базовую команду PyInstaller из конфига.

    Build base PyInstaller command from config.
    """
    pi_cfg = _cfg.get("pyinstaller", {})
    icon = get_icon_path("windows" if sys.platform == "win32" else
                         "macos" if sys.platform == "darwin" else "linux")

    cmd = [
        python, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--distpath", str(DIST_DIR),
        "--clean",
    ]

    if pi_cfg.get("onefile", True):
        cmd.append("--onefile")

    if pi_cfg.get("windowed", True) and sys.platform == "win32":
        cmd.append("--windowed")

    if icon:
        cmd.extend(["--icon", str(icon)])
        log(f"Icon: {icon}")

    if INI_FILE.exists():
        sep = ";" if sys.platform == "win32" else ":"
        cmd.extend(["--add-data", f"{INI_FILE}{sep}."])

    if extra:
        cmd.extend(extra)

    cmd.append(str(PROJECT_ROOT / ENTRY_POINT))
    return cmd


# ---------------------------------------------------------------------------
# Сборка Windows / Windows build
# ---------------------------------------------------------------------------

def build_windows(python: Path, mode: str = "both") -> None:
    """Сборка под Windows / Build for Windows.

    Args:
        python: Путь к Python / Path to Python.
        mode: 'portable', 'installer' или 'both' (по умолчанию).
    """
    log("=== Building for Windows ===")

    clean_dirs(DIST_DIR / APP_NAME, DIST_DIR / f"{APP_NAME}.exe")

    # Сначала всегда собираем .exe / Always build .exe first
    cmd = _build_pyinstaller_cmd(python)
    run(cmd)

    exe_path = DIST_DIR / f"{APP_NAME}.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        log(f"Portable exe: {exe_path} ({size_mb:.1f} MB)")

    # Установщик / Installer
    if mode in ("installer", "both"):
        build_windows_installer()


def _find_iscc() -> str | None:
    """Ищет iscc.exe в PATH и стандартных каталогах установки.

    Search for iscc.exe in PATH and common install directories.
    Поддерживает Inno Setup 5/6/7.
    """
    # Сначала ищем в PATH / First check PATH
    found = shutil.which("iscc")
    if found:
        return found

    # Стандартные каталоги установки / Common install directories
    candidates = []
    for prog_dir in [
        os.environ.get("ProgramFiles", r"C:\Program Files"),
        os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
        os.environ.get("LOCALAPPDATA", ""),
    ]:
        if not prog_dir:
            continue
        base = Path(prog_dir)
        # Ищем папки "Inno Setup *" / Search for "Inno Setup *" folders
        for d in base.iterdir():
            if d.is_dir() and d.name.lower().startswith("inno setup"):
                candidates.append(d / "ISCC.exe")
                candidates.append(d / "iscc.exe")
        # Точное имя для Inno Setup 7 / Exact name for Inno Setup 7
        candidates.append(base / "Inno Setup 7" / "ISCC.exe")
        candidates.append(base / "Inno Setup 6" / "ISCC.exe")
        candidates.append(base / "Inno Setup 5" / "ISCC.exe")

    for path in candidates:
        if path.exists():
            return str(path)

    return None


def build_windows_installer() -> None:
    """Сборка установщика через Inno Setup."""
    iscc = _find_iscc()
    if not iscc:
        log("Inno Setup (iscc) not found. Skipping installer build.")
        log("Install from: https://jrsoftware.org/isinfo.php")
        log("Or add ISCC.exe to PATH.")
        return

    iss_script = BUILD_DIR / "inno_setup" / "installer_questions.iss"
    if not iss_script.exists():
        log(f"ISS script not found: {iss_script}")
        return

    log("Building installer with Inno Setup...")
    import re
    # VersionInfoVersion требует X.Y.Z.W (только цифры)
    # VersionInfoVersion requires X.Y.Z.W (digits only)
    nums = re.findall(r"\d+", VERSION)
    info_version = ".".join(nums[:4]) if nums else "0.0.0.0"
    cmd = [
        iscc,
        f"/DMyAppVersion={VERSION}",
        f"/DMyInfoVersion={info_version}",
        str(iss_script),
    ]
    log(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=str(BUILD_DIR / "inno_setup"),
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        for line in result.stdout.strip().splitlines():
            log(f"  {line}")
    if result.stderr.strip():
        for line in result.stderr.strip().splitlines():
            log(f"  {line}")
    if result.returncode != 0:
        log(f"Inno Setup failed with exit code {result.returncode}")
        sys.exit(1)

    installer = INSTALLER_DIR / f"{APP_NAME}-setup-{VERSION}.exe"
    if installer.exists():
        size_mb = installer.stat().st_size / (1024 * 1024)
        log(f"Installer: {installer} ({size_mb:.1f} MB)")


# ---------------------------------------------------------------------------
# Сборка Linux / Linux build
# ---------------------------------------------------------------------------

def build_linux(python: Path) -> None:
    """Сборка под Linux / Build for Linux."""
    log("=== Building for Linux ===")

    clean_dirs(DIST_DIR / APP_NAME)

    extra = []
    if _cfg.get("linux", {}).get("strip_binary", True):
        extra.append("--strip")

    cmd = _build_pyinstaller_cmd(python, extra=extra)
    run(cmd)

    binary = DIST_DIR / APP_NAME
    if binary.exists():
        size_mb = binary.stat().st_size / (1024 * 1024)
        log(f"Binary: {binary} ({size_mb:.1f} MB)")
        binary.chmod(binary.stat().st_mode | 0o755)


# ---------------------------------------------------------------------------
# Сборка macOS / macOS build
# ---------------------------------------------------------------------------

def build_macos(python: Path) -> None:
    """Сборка под macOS / Build for macOS."""
    log("=== Building for macOS ===")

    clean_dirs(DIST_DIR / f"{APP_NAME}.app", DIST_DIR / APP_NAME)

    cmd = _build_pyinstaller_cmd(python)
    run(cmd)

    app_bundle = DIST_DIR / f"{APP_NAME}.app"
    binary = DIST_DIR / APP_NAME

    target = app_bundle if app_bundle.exists() else binary
    if target.exists():
        if target.is_file():
            size_mb = target.stat().st_size / (1024 * 1024)
            log(f"Binary: {target} ({size_mb:.1f} MB)")
        else:
            size_mb = sum(f.stat().st_size for f in target.rglob("*") if f.is_file()) / (1024 * 1024)
            # .app bundle — multiple files, zip it
            archive = DIST_DIR / f"{APP_NAME}-{VERSION}-macos-portable.zip"
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
                for file in app_bundle.rglob("*"):
                    if file.is_file():
                        zf.write(file, f"{APP_NAME}.app/{file.relative_to(app_bundle)}")
            log(f"Archive: {archive} ({size_mb:.1f} MB)")


# ---------------------------------------------------------------------------
# Точка входа / Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Главный метод скрипта сборки / Main build script method."""
    parser = argparse.ArgumentParser(description=f"Build {APP_NAME}")
    parser.add_argument("--platform", choices=["windows", "linux", "macos"],
                        help="Target platform")
    parser.add_argument("--all", action="store_true",
                        help="Build for the current platform")
    parser.add_argument("--mode", choices=["portable", "installer", "both"],
                        default="both",
                        help="Build mode: portable, installer, or both (default: both)")
    parser.add_argument("--version", required=True,
                        help="Version string (e.g. 1.0.0)")
    parser.add_argument("--no-venv", action="store_true",
                        help="Skip virtual environment creation")
    args = parser.parse_args()

    global VERSION
    VERSION = args.version

    # Без аргументов — собираем для текущей платформы
    # No args — build for the current platform
    current = platform.system().lower()
    if current == "darwin":
        current = "macos"
    if not args.platform and not args.all:
        args.all = True

    target = current if args.all else args.platform

    if current != target and not args.all:
        log(f"Warning: Cross-compilation from {current} to {target} is not supported.")
        log("Building for the current platform instead.")
        target = current

    if args.no_venv:
        python = Path(sys.executable)
    else:
        python = ensure_venv()
        install_deps(python)

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    INSTALLER_DIR.mkdir(parents=True, exist_ok=True)

    if target == "windows":
        build_windows(python, mode=args.mode)
    elif target == "linux":
        build_linux(python)
    elif target == "macos":
        build_macos(python)
    else:
        log(f"Unknown platform: {target}")
        sys.exit(1)

    log("=== Build complete ===")


if __name__ == "__main__":
    main()
