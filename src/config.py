"""Константы, настройки по умолчанию и пресеты tessellation.

Constants, default settings, and tessellation presets.
"""

import os
import sys
import tempfile

# ---------------------------------------------------------------------------
# Поддерживаемые расширения файлов / Supported file extensions
# ---------------------------------------------------------------------------

STEP_EXTS = frozenset({".stp", ".step"})
IGES_EXTS = frozenset({".igs", ".iges"})
ALL_EXTS = STEP_EXTS | IGES_EXTS
ALL_EXTS_LIST = sorted(ALL_EXTS)

# Фильтры для диалога выбора файлов / File-dialog filters
FILETYPES = [
    ("CAD files", " ".join(f"*{e}" for e in ALL_EXTS_LIST)),
    ("STEP", "*.stp *.step"),
    ("IGES", "*.igs *.iges"),
    ("All files", "*.*"),
]

# ---------------------------------------------------------------------------
# Пресеты tessellation / Tessellation presets
# Каждый пресет — кортеж (linear_deflection, angular_deflection).
# Each preset is a (linear_deflection, angular_deflection) tuple.
# ---------------------------------------------------------------------------

PRESETS = {
    "draft":  (1.0,   1.0),
    "normal": (0.1,   0.5),
    "high":   (0.01,  0.2),
    "ultra":  (0.001, 0.1),
}

# ---------------------------------------------------------------------------
# Текст подсказки для зоны drag-and-drop / Drop-zone hint text
# ---------------------------------------------------------------------------

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES  # noqa: F401
    HAS_DND = True
except ImportError:
    HAS_DND = False

DROP_TIP = (
    "Drag & drop STEP / IGES file here" if HAS_DND
    else "Click Browse to select file"
)

# ---------------------------------------------------------------------------
# Рабочая директория приложения и INI-файл / App directory and INI file
# ---------------------------------------------------------------------------

# Определяем корневую директорию приложения (работает и для .exe, и для .py).
# Determine the application root directory (works for both .exe and .py).
if getattr(sys, "frozen", False):
    # PyInstaller: sys.executable — путь к .exe
    # PyInstaller: sys.executable points to the .exe
    APP_DIR = os.path.dirname(sys.executable)
else:
    # config.py лежит в src/, корень проекта — на уровень выше.
    # config.py lives in src/; the project root is one level up.
    APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INI_PATH = os.path.join(APP_DIR, "step2glb.ini")

# Базовая папка для временных сессий / Base folder for temporary sessions
BASE_TEMP = os.path.join(tempfile.gettempdir(), "step2glb")

# ---------------------------------------------------------------------------
# Настройки по умолчанию / Default settings
# ---------------------------------------------------------------------------

DEFAULTS = {
    "preset":   "draft",
    "lin":      "1.0",
    "ang":      "1.0",
    "relative": "false",
    "merge":    "true",
    "parallel": "true",
    "buffer":   "auto",
    "compress": "true",
}

# Размер буфера для gzip-сжатия (1 МБ) / Buffer size for gzip compression (1 MB)
GZIP_BUFFER_SIZE = 1048576

# Порог размера файла для предупреждения о долгой конвертации / Large file threshold (MB)
LARGE_FILE_THRESHOLD_MB = 500
