"""Вспомогательные функции: управление сессиями, I/O настроек, проверка путей.

Helper functions: session management, settings I/O, path checks.
"""

import configparser
import os
import shutil

from .config import APP_DIR, BASE_TEMP, DEFAULTS, INI_PATH


# ---------------------------------------------------------------------------
# Управление временными сессиями / Temporary session management
# ---------------------------------------------------------------------------

def is_pid_alive(pid: int) -> bool:
    """Проверяет, работает ли процесс с указанным PID.

    Check whether the process with the given PID is still running.
    """
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def cleanup_stale_sessions() -> None:
    """Удаляет устаревшие временные каталоги аварийно завершённых сессий.

    Remove stale temporary directories left by crashed previous sessions.
    """
    if not os.path.isdir(BASE_TEMP):
        return

    current_pid = os.getpid()
    for name in os.listdir(BASE_TEMP):
        dirpath = os.path.join(BASE_TEMP, name)
        if not os.path.isdir(dirpath):
            continue
        try:
            pid = int(name)
        except ValueError:
            continue
        if pid == current_pid or not is_pid_alive(pid):
            shutil.rmtree(dirpath, ignore_errors=True)


def get_session_dir() -> str:
    """Создаёт и возвращает каталог текущей сессии (PID-based).

    Create and return the temporary directory for the current session.
    """
    d = os.path.join(BASE_TEMP, str(os.getpid()))
    os.makedirs(d, exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# Чтение / запись настроек INI / INI settings read / write
# ---------------------------------------------------------------------------

def load_settings(cfg: configparser.ConfigParser) -> None:
    """Загружает настройки из INI-файла или устанавливает значения по умолчанию.

    Load settings from the INI file, or apply defaults if the file is absent.
    """
    if not os.path.isfile(INI_PATH):
        for key, value in DEFAULTS.items():
            cfg.set("main", key, value)
        return
    cfg.read(INI_PATH, encoding="utf-8")


def save_settings(cfg: configparser.ConfigParser) -> None:
    """Сохраняет текущие настройки в INI-файл.

    Write the current settings to the INI file.
    """
    with open(INI_PATH, "w", encoding="utf-8") as fh:
        cfg.write(fh)


# ---------------------------------------------------------------------------
# Работа с кодировкой путей / Path-encoding helpers
# ---------------------------------------------------------------------------

def has_non_ascii(path: str) -> bool:
    """Возвращает True, если путь содержит символы вне ASCII (например, кириллица).

    Return True if *path* contains non-ASCII characters (e.g. Cyrillic).
    cascadio cannot handle such paths, so a temp-copy workaround is needed.
    """
    try:
        path.encode("ascii")
        return False
    except UnicodeEncodeError:
        return True
