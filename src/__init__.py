"""Пакет step2glb / step2glb package.

Преобразователь файлов STEP/IGES в формат GLB.
STEP/IGES to GLB converter.

Версия читается из build/build_config.json.
Version is read from build/build_config.json.
"""

import json
from pathlib import Path


def _read_version() -> str:
    """Читает версию из build_config.json.

    Read version from build_config.json.

    Fallback на hardcoded значение, если файл не найден.
    Falls back to hardcoded value if the file is missing.
    """
    try:
        # src/__init__.py → src/ → project root → build/build_config.json
        config_path = Path(__file__).resolve().parent.parent / "build" / "build_config.json"
        if config_path.exists():
            with open(config_path, encoding="utf-8") as fh:
                return json.load(fh)["version"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        pass
    return "1.0.0"


__version__ = _read_version()
__author__ = "step2glb contributors"
