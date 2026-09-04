#!/usr/bin/env python3
"""Загрузчик конфигурации сборки.

Build configuration loader.

Читает build/build_config.json и возвращает его как словарь.
Reads build/build_config.json and returns it as a dict.

Использование / Usage:
    from _config_loader import load_build_config
    cfg = load_build_config()
    print(cfg["app_name"], cfg["version"])
"""

import json
from pathlib import Path

_CONFIG_CACHE: dict | None = None


def load_build_config() -> dict:
    """Загружает конфигурацию сборки из build_config.json.

    Load build configuration from build_config.json.

    Возвращает кэшированный словарь / Returns cached dict.
    Повторные вызовы не перечитывают файл / Subsequent calls reuse the cache.
    """
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    config_path = Path(__file__).resolve().parent / "build_config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Build config not found: {config_path}")

    with open(config_path, encoding="utf-8") as fh:
        _CONFIG_CACHE = json.load(fh)

    return _CONFIG_CACHE


def get_icon_path(platform: str = "windows") -> Path | None:
    """Возвращает путь к иконке для указанной платформы.

    Return icon path for the given platform.

    Args:
        platform: 'windows', 'macos' или 'linux'.

    Returns:
        Path к иконке или None, если не найдена.
    """
    cfg = load_build_config()
    project_root = Path(__file__).resolve().parent.parent

    icon_key = "icons"
    icons = cfg.get(icon_key, {})

    if platform == "windows":
        fname = icons.get("windows", "icon.ico")
    elif platform == "macos":
        fname = icons.get("macos", "icon.icns")
    elif platform == "linux":
        fname = icons.get("linux", "icon.png")
    else:
        return None

    icon_path = project_root / fname
    return icon_path if icon_path.exists() else None


def get_project_root() -> Path:
    """Возвращает корень проекта / Return project root directory."""
    return Path(__file__).resolve().parent.parent
