# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for step2glb
# Генерируется автоматически, но может быть использован напрямую.
# Auto-generated but can also be used directly.

import os
import sys
from pathlib import Path

block_cipher = None

# Корневая директория проекта / Project root directory
PROJECT_ROOT = Path(SPECPATH).parent.parent

a = Analysis(
    [str(PROJECT_ROOT / "main.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Сборка: onefile или onedir / Build: onefile or onedir
# Раскомментируйте нужный вариант / Uncomment the desired option

# --- Вариант 1: Один файл (рекомендуется для портативной сборки)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="step2glb",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,           # True = консоль включена / True = console enabled
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="icon.ico",       # Раскомментируйте для иконки / Uncomment for icon
)

# --- Вариант 2: Папка (быстрый запуск, удобно для отладки)
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name="step2glb",
# )
