"""Точка входа приложения step2glb.

Entry point for the step2glb application.
"""

import multiprocessing

from .utils import cleanup_stale_sessions
from .app import App


def main() -> None:
    """Запуск GUI-приложения / Launch the GUI application."""
    multiprocessing.freeze_support()
    cleanup_stale_sessions()
    App().mainloop()


if __name__ == "__main__":
    main()
