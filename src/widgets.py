"""Пользовательские виджеты GUI / Custom GUI widgets."""

import tkinter as tk


class Tooltip:
    """Всплывающая подсказка для виджетов Tkinter с задержкой.

    Delayed tooltip widget for Tkinter elements.
    """

    def __init__(self, widget: tk.Widget, text: str, delay: int = 400) -> None:
        """
        Args:
            widget: Целевой виджет / Target widget.
            text:   Текст подсказки / Tooltip text.
            delay:  Задержка показа (мс) / Show delay in milliseconds.
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self._tip_win: tk.Toplevel | None = None
        self._after_id: str | None = None

        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")
        widget.bind("<ButtonPress>", self._on_leave, add="+")

    # ------------------------------------------------------------------
    # Обработчики событий / Event handlers
    # ------------------------------------------------------------------

    def _on_enter(self, event: tk.Event | None = None) -> None:
        """Начало отсчёта задержки перед показом / Start delay countdown."""
        self._after_id = self.widget.after(self.delay, self._show)

    def _on_leave(self, event: tk.Event | None = None) -> None:
        """Отмена показа и скрытие подсказки / Cancel and hide tooltip."""
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        self._hide()

    def _show(self) -> None:
        """Отображает всплывающее окно подсказки / Show the tooltip window."""
        if self._tip_win:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4

        self._tip_win = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.configure(bg="#ffffdd")

        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#ffffdd",
            foreground="#333",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 9),
            padx=8,
            pady=4,
            wraplength=380,
        )
        label.pack()

    def _hide(self) -> None:
        """Скрывает всплывающее окно / Hide the tooltip window."""
        if self._tip_win:
            self._tip_win.destroy()
            self._tip_win = None
