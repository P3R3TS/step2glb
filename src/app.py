"""Главное окно приложения (GUI).

Main application window (Tkinter GUI).
"""

import configparser
import multiprocessing
import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from .config import (
    ALL_EXTS,
    ALL_EXTS_LIST,
    BASE_TEMP,
    DEFAULTS,
    DROP_TIP,
    FILETYPES,
    HAS_DND,
    PRESETS,
)
from .utils import get_session_dir, load_settings, save_settings
from .widgets import Tooltip
from .worker import _worker

# Опциональная поддержка drag-and-drop / Optional drag-and-drop support
if HAS_DND:
    from tkinterdnd2 import DND_FILES  # noqa: F401


_BaseClass = tk.Tk
if HAS_DND:
    try:
        from tkinterdnd2.TkinterDnD import Tk as DnDTk
        _BaseClass = DnDTk
    except (ImportError, AttributeError):
        pass


class App(_BaseClass):
    """Основное окно приложения STEP/IGES -> GLB.

    Main application window for STEP/IGES -> GLB conversion.
    """

    # ------------------------------------------------------------------
    # Инициализация / Initialization
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        super().__init__()

        self._session_dir = get_session_dir()
        self._cfg = configparser.ConfigParser()
        self._cfg.add_section("main")
        load_settings(self._cfg)

        self.title("STEP/IGES \u2192 GLB")
        self.geometry("740x700")
        self.minsize(620, 580)
        self.configure(bg="#f0f0f0")

        self._converting = False
        self._worker_proc: multiprocessing.Process | None = None
        self._worker_queue: multiprocessing.Queue | None = None

        self._build_ui()
        self._apply_settings()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # Построение интерфейса / Build the UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Создаёт все элементы интерфейса / Create all UI elements."""
        self._configure_styles()

        self._build_input_section()
        self._build_drop_zone()
        self._build_settings_section()
        self._build_output_section()
        self._build_convert_button()
        self._build_progress_section()

    def _configure_styles(self) -> None:
        """Настраивает виджет-стили ttk / Configure ttk widget styles."""
        style = ttk.Style(self)
        style.configure("TLabel", background="#f0f0f0")
        style.configure("TButton", padding=5)
        style.configure(
            "Drop.TLabel",
            font=("Segoe UI", 11),
            foreground="#666",
            background="#e8e8e8",
            anchor="center",
            padding=18,
        )
        style.configure(
            "DropActive.TLabel",
            font=("Segoe UI", 11),
            foreground="#2266cc",
            background="#d0e4ff",
            anchor="center",
            padding=18,
        )

    # --- Блок ввода / Input section ---

    def _build_input_section(self) -> None:
        """Секция выбора входного файла / Input file selection section."""
        frame = ttk.LabelFrame(self, text="  Input file  ", padding=8)
        frame.pack(fill="x", padx=10, pady=(10, 4))

        self.var_input = tk.StringVar()
        entry = ttk.Entry(
            frame,
            textvariable=self.var_input,
            state="readonly",
            font=("Consolas", 9),
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(frame, text="Browse\u2026", command=self._browse_input).pack(
            side="right"
        )

    # --- Зона drag-and-drop / Drop zone ---

    def _build_drop_zone(self) -> None:
        """Визуальная зона для drag-and-drop файлов / Visual drag-and-drop zone."""
        self.drop_label = ttk.Label(
            self,
            text=DROP_TIP,
            style="Drop.TLabel",
            relief="groove",
            borderwidth=2,
        )
        self.drop_label.pack(fill="x", padx=10, pady=4, ipady=8)

        if HAS_DND:
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind("<<DropEnter>>", self._on_drop_enter)
            self.drop_label.dnd_bind("<<DropLeave>>", self._on_drop_leave)
            self.drop_label.dnd_bind("<<Drop>>", self._on_drop)
            self.drop_target_register(DND_FILES)
            self.dnd_bind("<<Drop>>", self._on_drop)

    # --- Блок настроек / Settings section ---

    def _build_settings_section(self) -> None:
        """Секция параметров tessellation / Tessellation settings section."""
        frame = ttk.LabelFrame(self, text="  Settings  ", padding=8)
        frame.pack(fill="x", padx=10, pady=4)

        self._build_preset_row(frame)
        self._build_tolerance_row(frame)
        self._build_checkbox_row(frame)
        self._build_buffer_row(frame)

    def _build_preset_row(self, parent: tk.Widget) -> None:
        """Строка пресетов / Preset row."""
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=2)

        lbl = ttk.Label(row, text="Preset:")
        lbl.pack(side="left")
        Tooltip(
            lbl,
            "Ready-made detail level.\n"
            "draft \u2014 fast, coarse mesh (preview)\n"
            "normal \u2014 balanced\n"
            "high \u2014 detailed, slower\n"
            "ultra \u2014 maximum quality, very slow",
        )

        self.var_preset = tk.StringVar(value="draft")
        for name in ("draft", "normal", "high", "ultra"):
            ttk.Radiobutton(
                row,
                text=name,
                variable=self.var_preset,
                value=name,
                command=self._on_preset,
            ).pack(side="left", padx=6)

    def _build_tolerance_row(self, parent: tk.Widget) -> None:
        """Строка допусков tessellation / Tolerance row."""
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=2)

        # Linear deflection
        lbl_lin = ttk.Label(row, text="Lin:")
        lbl_lin.pack(side="left")
        Tooltip(
            lbl_lin,
            "Linear deflection \u2014 max distance between the real surface\n"
            "and the triangle mesh. Lower = more triangles = finer detail.\n"
            "0.001 = ultra fine, 0.01 = high, 0.1 = normal, 1.0 = draft",
        )
        self.var_lin = tk.DoubleVar(value=1.0)
        ttk.Spinbox(
            row,
            from_=0.0001,
            to=10.0,
            increment=0.01,
            textvariable=self.var_lin,
            width=8,
            format="%.4f",
        ).pack(side="left", padx=(2, 14))

        # Angular deflection
        lbl_ang = ttk.Label(row, text="Ang:")
        lbl_ang.pack(side="left")
        Tooltip(
            lbl_ang,
            "Angular deflection \u2014 max angle (radians) between normals\n"
            "of adjacent triangles. Lower = smoother curves.\n"
            "0.1 = ultra fine, 0.2 = high, 0.5 = normal, 1.0 = draft",
        )
        self.var_ang = tk.DoubleVar(value=1.0)
        ttk.Spinbox(
            row,
            from_=0.01,
            to=10.0,
            increment=0.1,
            textvariable=self.var_ang,
            width=8,
            format="%.2f",
        ).pack(side="left", padx=2)

    def _build_checkbox_row(self, parent: tk.Widget) -> None:
        """Строка флажков: Relative, Merge, Parallel / Checkbox row."""
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=2)

        # Relative
        self.var_relative = tk.BooleanVar()
        cb_rel = ttk.Checkbutton(row, text="Relative", variable=self.var_relative)
        cb_rel.pack(side="left")
        Tooltip(
            cb_rel,
            "When ON, linear deflection is relative to each edge length\n"
            "(percentage). When OFF, it is an absolute distance in model units.",
        )

        # Merge
        self.var_merge = tk.BooleanVar(value=True)
        cb_merge = ttk.Checkbutton(row, text="Merge", variable=self.var_merge)
        cb_merge.pack(side="left", padx=10)
        Tooltip(
            cb_merge,
            "Merge all triangle faces of a part into a single mesh primitive.\n"
            "ON = one mesh per part (smaller file, simpler structure).\n"
            "OFF = each face is a separate primitive (more nodes in glTF).",
        )

        # Parallel
        self.var_parallel = tk.BooleanVar(value=True)
        cb_par = ttk.Checkbutton(row, text="Parallel", variable=self.var_parallel)
        cb_par.pack(side="left", padx=10)
        Tooltip(
            cb_par,
            "Use all CPU cores for tessellation.\n"
            "ON = faster on multi-core CPUs.\n"
            "OFF = single-threaded, uses less RAM.",
        )

    def _build_buffer_row(self, parent: tk.Widget) -> None:
        """Строка стратегии буфера и gzip / Buffer strategy and gzip row."""
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=2)

        lbl_buf = ttk.Label(row, text="Buffer:")
        lbl_buf.pack(side="left")
        Tooltip(
            lbl_buf,
            "Memory overflow strategy for large files (>500 MB).\n"
            "auto  \u2014 disk buffer when file > 500 MB\n"
            "disk  \u2014 always write temp file to reduce RAM\n"
            "none  \u2014 keep everything in RAM\n"
            "force \u2014 always use disk, even for small files",
        )
        self.var_buffer = tk.StringVar(value="auto")
        ttk.Combobox(
            row,
            textvariable=self.var_buffer,
            values=["auto", "disk", "none", "force"],
            state="readonly",
            width=8,
        ).pack(side="left", padx=(2, 14))

        self.var_compress = tk.BooleanVar(value=True)
        cb_gz = ttk.Checkbutton(row, text="Gzip", variable=self.var_compress)
        cb_gz.pack(side="left")
        Tooltip(
            cb_gz,
            "Compress the output GLB with gzip.\n"
            "Produces a .glb.gz file, typically 30\u201370% smaller.\n"
            "Supported by most 3D viewers and web loaders.",
        )

    # --- Блок вывода / Output section ---

    def _build_output_section(self) -> None:
        """Секция выбора выходного файла / Output file selection section."""
        frame = ttk.LabelFrame(self, text="  Output file  ", padding=8)
        frame.pack(fill="x", padx=10, pady=4)

        self.var_output = tk.StringVar()
        entry = ttk.Entry(
            frame,
            textvariable=self.var_output,
            state="readonly",
            font=("Consolas", 9),
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(frame, text="Browse\u2026", command=self._browse_output).pack(
            side="right"
        )

    # --- Кнопка конвертации / Convert button ---

    def _build_convert_button(self) -> None:
        """Кнопка запуска конвертации / Conversion start button."""
        self.btn_convert = ttk.Button(
            self, text="\u25b6  Convert", command=self._start_convert
        )
        self.btn_convert.pack(fill="x", padx=10, pady=6)

    # --- Блок прогресса / Progress section ---

    def _build_progress_section(self) -> None:
        """Секция индикатора прогресса и лога / Progress bar and log section."""
        frame = ttk.LabelFrame(self, text="  Progress  ", padding=8)
        frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Прогресс-бар / Progress bar
        self.progress = ttk.Progressbar(frame, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(0, 4))

        # Статус / Status label
        self.var_status = tk.StringVar(value="Ready")
        ttk.Label(frame, textvariable=self.var_status, anchor="w").pack(fill="x")

        # Консоль лога / Log console
        self.log = tk.Text(
            frame,
            height=14,
            state="disabled",
            wrap="word",
            font=("Consolas", 9),
            bg="#1a1a2e",
            fg="#d4d4d4",
            insertbackground="#d4d4d4",
            relief="flat",
            borderwidth=2,
            selectbackground="#264f78",
        )
        sb = ttk.Scrollbar(frame, command=self.log.yview)
        self.log.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log.pack(fill="both", expand=True)

        # Цветовые теги лога / Log color tags
        for tag, fg in [
            ("info", "#d4d4d4"),
            ("ok", "#6a9955"),
            ("err", "#f44747"),
            ("warn", "#cca700"),
            ("dim", "#808080"),
            ("hi", "#569cd6"),
        ]:
            self.log.tag_configure(tag, foreground=fg)

        self._log(f"Ready.  {DROP_TIP}", "dim")

    # ------------------------------------------------------------------
    # Управление настройками / Settings management
    # ------------------------------------------------------------------

    def _apply_settings(self) -> None:
        """Применяет сохранённые настройки к элементам GUI.

        Apply saved settings to GUI widgets.
        """
        sec = self._cfg["main"]
        self.var_preset.set(sec.get("preset", DEFAULTS["preset"]))
        self.var_lin.set(float(sec.get("lin", DEFAULTS["lin"])))
        self.var_ang.set(float(sec.get("ang", DEFAULTS["ang"])))
        self.var_relative.set(sec.getboolean("relative", DEFAULTS["relative"]))
        self.var_merge.set(sec.getboolean("merge", DEFAULTS["merge"]))
        self.var_parallel.set(sec.getboolean("parallel", DEFAULTS["parallel"]))
        self.var_buffer.set(sec.get("buffer", DEFAULTS["buffer"]))
        self.var_compress.set(sec.getboolean("compress", DEFAULTS["compress"]))

    def _collect_settings(self) -> None:
        """Собирает текущие значения GUI в объект настроек.

        Collect current GUI values into the settings object.
        """
        sec = self._cfg["main"]
        sec["preset"] = self.var_preset.get()
        sec["lin"] = str(self.var_lin.get())
        sec["ang"] = str(self.var_ang.get())
        sec["relative"] = str(self.var_relative.get()).lower()
        sec["merge"] = str(self.var_merge.get()).lower()
        sec["parallel"] = str(self.var_parallel.get()).lower()
        sec["buffer"] = self.var_buffer.get()
        sec["compress"] = str(self.var_compress.get()).lower()

    # ------------------------------------------------------------------
    # Drag-and-drop обработчики / Drag-and-drop handlers
    # ------------------------------------------------------------------

    def _on_drop_enter(self, event: tk.Event) -> None:
        """Визуальная подсветка при входе в зону / Highlight on drop-enter."""
        self.drop_label.configure(style="DropActive.TLabel")

    def _on_drop_leave(self, event: tk.Event) -> None:
        """Снятие подсветки при выходе из зоны / Remove highlight on drop-leave."""
        self.drop_label.configure(style="Drop.TLabel")

    def _on_drop(self, event: tk.Event) -> None:
        """Обработка drop-события / Handle a drop event."""
        self.drop_label.configure(style="Drop.TLabel")
        files = self.tk.splitlist(event.data)
        if files:
            self._set_input(files[0])

    # ------------------------------------------------------------------
    # Выбор файлов / File selection
    # ------------------------------------------------------------------

    def _set_input(self, path: str) -> None:
        """Устанавливает входной файл с валидацией.

        Set the input file with validation.
        """
        path = path.strip()

        # Удаление обрамляющих фигурных скобок (Windows-specific)
        # Strip surrounding braces (Windows drag-and-drop quirk).
        if os.name == "nt" and path.startswith("{") and path.endswith("}"):
            path = path[1:-1]

        ext = os.path.splitext(path)[1].lower()
        if ext not in ALL_EXTS:
            messagebox.showerror(
                "Unsupported",
                f"Cannot open {ext}\nUse: {', '.join(ALL_EXTS_LIST)}",
            )
            return
        if not os.path.isfile(path):
            messagebox.showerror("Not found", path)
            return

        self.var_input.set(path)
        if not self.var_output.get():
            self.var_output.set(os.path.splitext(path)[0] + ".glb")

    def _browse_input(self) -> None:
        """Диалог выбора входного файла / Open input file dialog."""
        path = filedialog.askopenfilename(filetypes=FILETYPES)
        if path:
            self._set_input(path)

    def _browse_output(self) -> None:
        """Диалог выбора выходного файла / Open output file dialog."""
        init_dir = os.path.dirname(self.var_input.get()) or os.getcwd()
        init_file = os.path.basename(self.var_output.get()) or "output.glb"
        path = filedialog.asksaveasfilename(
            initialdir=init_dir,
            initialfile=init_file,
            defaultextension=".glb",
            filetypes=[("GLB", "*.glb"), ("All", "*.*")],
        )
        if path:
            self.var_output.set(path)

    # ------------------------------------------------------------------
    # Пресеты / Presets
    # ------------------------------------------------------------------

    def _on_preset(self) -> None:
        """Применяет выбранный пресет к полям допусков.

        Apply the selected preset to the tolerance fields.
        """
        lin, ang = PRESETS[self.var_preset.get()]
        self.var_lin.set(lin)
        self.var_ang.set(ang)

    # ------------------------------------------------------------------
    # Лог и прогресс / Log and progress
    # ------------------------------------------------------------------

    def _log(self, msg: str, tag: str = "info") -> None:
        """Добавляет строку в консоль лога / Append a line to the log console."""
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self) -> None:
        """Очищает консоль лога / Clear the log console."""
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _pulse_start(self) -> None:
        """Запускает неопределённый прогресс-бар / Start indeterminate progress."""
        self.progress.configure(mode="indeterminate")
        self.progress.start(15)

    def _pulse_stop(self) -> None:
        """Останавливает прогресс-бар / Stop the progress bar."""
        self.progress.stop()
        self.progress.configure(mode="determinate", value=0)

    # ------------------------------------------------------------------
    # Запуск конвертации / Start conversion
    # ------------------------------------------------------------------

    def _start_convert(self) -> None:
        """Запускает конвертацию в фоновом процессе.

        Start the conversion in a background multiprocessing.Process.
        """
        if self._converting:
            return

        inp = self.var_input.get()
        out = self.var_output.get()

        if not inp or not os.path.isfile(inp):
            messagebox.showerror("Error", "Select a valid input file")
            return
        if not out:
            messagebox.showerror("Error", "Select output file path")
            return

        self._converting = True
        self.btn_convert.configure(state="disabled")
        self._clear_log()
        self.var_status.set("Starting\u2026")
        self._pulse_start()

        ext = os.path.splitext(inp)[1].lower()
        file_type = "iges" if ext in (".igs", ".iges") else "step"

        self._worker_queue = multiprocessing.Queue()

        self._worker_proc = multiprocessing.Process(
            target=_worker,
            args=(
                self._worker_queue,
                self._session_dir,
                inp,
                out,
                self.var_lin.get(),
                self.var_ang.get(),
                self.var_relative.get(),
                self.var_merge.get(),
                self.var_parallel.get(),
                file_type,
                self.var_compress.get(),
            ),
            daemon=True,
        )
        self._worker_proc.start()
        self._poll_queue()

    # ------------------------------------------------------------------
    # Опрос очереди / Queue polling
    # ------------------------------------------------------------------

    def _poll_queue(self) -> None:
        """Опрашивает очередь сообщений от воркера (каждые 100 мс).

        Poll the worker message queue every 100 ms.
        """
        if self._worker_queue is None:
            return

        try:
            while True:
                msg = self._worker_queue.get_nowait()
                self._handle_msg(msg)
        except Exception:
            pass

        if self._worker_proc and self._worker_proc.is_alive():
            self.after(100, self._poll_queue)
        else:
            self._finish_convert()

    def _handle_msg(self, msg: dict) -> None:
        """Обрабатывает сообщение от воркера / Handle a message from the worker."""
        msg_type = msg.get("type")

        if msg_type == "status":
            self.var_status.set(msg["text"])
            self._log(msg["text"], "info")

        elif msg_type == "log":
            self._log(msg["text"], msg.get("tag", "info"))

        elif msg_type == "tess_done":
            dt = msg["time"]
            mb = msg["size"] / 1048576
            self._log(f"Tessellation: {dt:.1f}s, mesh: {mb:.1f} MB", "ok")
            self.var_status.set(f"Tessellation done in {dt:.1f}s")

        elif msg_type == "done":
            if "comp_mb" in msg:
                ratio = msg["comp_mb"] / msg["raw_mb"] * 100 if msg["raw_mb"] else 0
                self._log(
                    f"Compressed: {msg['comp_mb']:.1f} MB ({ratio:.0f}%)", "ok"
                )
            self._log(f"Done: {msg['path']}", "ok")
            self._log(f"Total: {msg['time']:.1f}s", "ok")
            self.var_status.set(f"Completed in {msg['time']:.1f}s")

        elif msg_type == "error":
            self._log(f"Error: {msg['text']}", "err")
            self.var_status.set("Failed")

    def _finish_convert(self) -> None:
        """Завершает конвертацию и восстанавливает UI.

        Finalize conversion and restore the UI state.
        """
        self._pulse_stop()
        self._converting = False

        if self._worker_proc:
            self._worker_proc.join(timeout=1)
            self._worker_proc = None

        self._worker_queue = None
        self.btn_convert.configure(state="normal")

    # ------------------------------------------------------------------
    # Закрытие приложения / Application shutdown
    # ------------------------------------------------------------------

    def _on_close(self) -> None:
        """Корректное завершение: сохранение настроек, очистка / Clean shutdown."""
        if self._converting:
            if not messagebox.askokcancel(
                "Quit", "Conversion is running. Quit anyway?"
            ):
                return
            if self._worker_proc and self._worker_proc.is_alive():
                self._worker_proc.terminate()
                self._worker_proc.join(timeout=3)

        self._collect_settings()
        save_settings(self._cfg)
        shutil.rmtree(self._session_dir, ignore_errors=True)
        shutil.rmtree(BASE_TEMP, ignore_errors=True)
        self.destroy()
