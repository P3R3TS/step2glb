#!/usr/bin/env python3
"""Скрипт сборки step2glb через PyInstaller.

PyInstaller build script for step2glb.

Конфигурация: build/build_config.json
Configuration: build/build_config.json

Использование / Usage:
    python build/pyinstaller/build_portable.py [--onedir] [--console]

Опции / Options:
    --onedir    Сборка в папку / Build to directory
    --console   Консольное окно для отладки / Console window for debugging
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Импорт загрузчика конфигурации / Import config loader
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _config_loader import load_build_config, get_icon_path, get_project_root

# ---------------------------------------------------------------------------
# Конфигурация / Configuration
# ---------------------------------------------------------------------------

_cfg = load_build_config()

PROJECT_ROOT = get_project_root()
MAIN_SCRIPT = PROJECT_ROOT / _cfg["entry_point"]
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build" / "pyinstaller"
SPEC_FILE = BUILD_DIR / f"{_cfg['app_name']}.spec"
INI_FILE = PROJECT_ROOT / _cfg["ini_file"]

APP_NAME = _cfg["app_name"]
APP_VERSION = _cfg["version"]


def build(onefile: bool = True, console: bool = False) -> None:
    """Запуск сборки через PyInstaller.

    Launch PyInstaller build.

    Args:
        onefile: Собрать в один файл / Build into single file.
        console: Показать консольное окно / Show console window.
    """
    print(f"[build] App:        {APP_NAME} v{APP_VERSION}")
    print(f"[build] Project:    {PROJECT_ROOT}")
    print(f"[build] Entry:      {MAIN_SCRIPT}")
    print(f"[build] Mode:       {'onefile' if onefile else 'onedir'}")
    print(f"[build] Console:    {console}")

    if not MAIN_SCRIPT.exists():
        print(f"[error] Main script not found: {MAIN_SCRIPT}")
        sys.exit(1)

    # Иконка / Icon
    icon_platform = "windows" if sys.platform == "win32" else \
                    "macos" if sys.platform == "darwin" else "linux"
    icon = get_icon_path(icon_platform)

    # Формируем команду / Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR / "build"),
        "--specpath", str(BUILD_DIR),
        "--clean",
    ]

    if onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    if not console:
        if sys.platform == "win32":
            cmd.append("--windowed")

    if icon:
        cmd.extend(["--icon", str(icon)])
        print(f"[build] Icon: {icon}")

    if INI_FILE.exists():
        sep = ";" if sys.platform == "win32" else ":"
        cmd.extend(["--add-data", f"{INI_FILE}{sep}."])
        print(f"[build] INI:  {INI_FILE}")

    cmd.append(str(MAIN_SCRIPT))

    print(f"\n[build] Command: {' '.join(cmd)}")
    print("[build] Starting build...\n")

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))

    if result.returncode != 0:
        print(f"\n[error] Build failed with exit code {result.returncode}")
        sys.exit(result.returncode)

    # Проверка результата / Verify output
    if onefile:
        suffix = ".exe" if sys.platform == "win32" else ""
        output = DIST_DIR / f"{APP_NAME}{suffix}"
    else:
        output = DIST_DIR / APP_NAME

    if output.exists():
        if output.is_file():
            size_mb = output.stat().st_size / (1024 * 1024)
        else:
            size_mb = sum(f.stat().st_size for f in output.rglob("*") if f.is_file()) / (1024 * 1024)
        print(f"\n[build] Build successful!")
        print(f"[build] Output: {output}")
        print(f"[build] Size:   {size_mb:.1f} MB")
    else:
        print(f"\n[warning] Output not found: {output}")


def main() -> None:
    """Точка входа / Entry point."""
    parser = argparse.ArgumentParser(description=f"Build {APP_NAME} with PyInstaller")
    parser.add_argument("--onedir", action="store_true",
                        help="Build to directory instead of single file")
    parser.add_argument("--console", action="store_true",
                        help="Enable console window for debugging")
    args = parser.parse_args()
    build(onefile=not args.onedir, console=args.console)


if __name__ == "__main__":
    main()
