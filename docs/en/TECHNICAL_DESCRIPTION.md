# Technical Description

## step2glb — STEP/IGES to GLB Converter

---

**Document version:** 1.0  
**Date:** September 2026  
**Applicable standards:** GOST 19.201-78, GOST 19.701-90  

---

## 1. Program Architecture

### 1.1. Overview

The application follows a **GUI + Worker Process** architecture. The main thread manages the GUI, while conversion runs in a separate process via `multiprocessing.Process`. Inter-process communication uses `multiprocessing.Queue`.

```
┌──────────────────────────────────────────────┐
│               GUI (main process)              │
│                                               │
│  ┌─────────┐  ┌──────────┐  ┌─────────────┐ │
│  │  Input   │  │ Settings │  │   Output    │ │
│  └────┬────┘  └────┬─────┘  └──────┬──────┘ │
│       │            │               │         │
│       └────────────┼───────────────┘         │
│                    │                          │
│           ┌────────▼────────┐                │
│           │   Convert btn   │                │
│           └────────┬────────┘                │
│                    │                          │
│     ┌──────────────▼──────────────┐          │
│     │  Queue (msg polling @100ms) │          │
│     └──────────────┬──────────────┘          │
│                    │                          │
│  ┌─────────────────▼─────────────────────┐  │
│  │  Progress bar  │  Status  │  Log      │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
                      │
              Queue (IPC)
                      │
┌─────────────────────▼────────────────────────┐
│          Worker Process (daemon)              │
│                                               │
│  ┌──────────────────────────────────────┐   │
│  │  1. Copy to temp (if non-ASCII)      │   │
│  │  2. cascadio.step_to_glb() / .load() │   │
│  │  3. (Optional) gzip compression      │   │
│  │  4. Send result to Queue             │   │
│  └──────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
```

### 1.2. Module Structure

| Module | Purpose | Responsibility |
|--------|---------|----------------|
| `config.py` | Constants | Extensions, presets, paths, defaults |
| `utils.py` | Utilities | Session management, settings I/O, path encoding checks |
| `worker.py` | Worker | Background conversion process via cascadio |
| `widgets.py` | Widgets | Custom `Tooltip` widget for Tkinter |
| `app.py` | Application | GUI: window, settings, log, progress |
| `main.py` | Entry point | `freeze_support()`, session cleanup, `App` launch |

---

## 2. Module Reference

### 2.1. config.py — Constants

**Purpose:** Stores all project constants.

| Symbol | Type | Description |
|--------|------|-------------|
| `STEP_EXTS` | `frozenset` | STEP file extensions |
| `IGES_EXTS` | `frozenset` | IGES file extensions |
| `ALL_EXTS` | `frozenset` | Union of STEP and IGES extensions |
| `ALL_EXTS_LIST` | `list` | Sorted list of extensions |
| `FILETYPES` | `list[tuple]` | File-dialog filters |
| `PRESETS` | `dict` | Tessellation presets |
| `HAS_DND` | `bool` | Whether drag-and-drop is available |
| `DROP_TIP` | `str` | Drop-zone hint text |
| `APP_DIR` | `str` | Application root directory |
| `INI_PATH` | `str` | Path to settings file |
| `BASE_TEMP` | `str` | Base folder for temporary sessions |
| `DEFAULTS` | `dict` | Default settings |
| `GZIP_BUFFER_SIZE` | `int` | Gzip buffer size (1 MB) |

### 2.2. utils.py — Utilities

| Function | Args | Returns | Description |
|----------|------|---------|-------------|
| `is_pid_alive(pid)` | `int` | `bool` | Check if process exists |
| `cleanup_stale_sessions()` | — | `None` | Remove stale temp directories |
| `get_session_dir()` | — | `str` | Create current session directory |
| `load_settings(cfg)` | `ConfigParser` | `None` | Load INI settings |
| `save_settings(cfg)` | `ConfigParser` | `None` | Save INI settings |
| `has_non_ascii(path)` | `str` | `bool` | Check for non-ASCII characters in path |

### 2.3. worker.py — Background Process

**Purpose:** Conversion in a child process.

The `_worker()` function:
- Receives conversion parameters as arguments.
- Sends status and log messages to GUI via `Queue`.
- Processes STEP via `cascadio.step_to_glb()`.
- Processes IGES via `cascadio.load()`.
- Optionally performs gzip compression.
- Automatically copies files to temp on non-ASCII paths.

**Message protocol:**

| Type | Keys | Description |
|------|------|-------------|
| `log` | `text`, `tag` | Log line |
| `status` | `text` | Current status |
| `tess_done` | `time`, `size` | Tessellation result |
| `done` | `path`, `time`, `raw_mb`, `comp_mb` | Conversion complete |
| `error` | `text` | Error |

### 2.4. widgets.py — Widgets

**Tooltip class:**
- Delayed popup tooltip for Tkinter widgets.
- Default delay: 400 ms (configurable).
- Positioning: below the widget.
- Auto-hide on mouse leave.

### 2.5. app.py — Main Window

| Method | Description |
|--------|-------------|
| `__init__()` | Window initialization, settings load |
| `_build_ui()` | Build all UI elements |
| `_apply_settings()` | Apply saved settings |
| `_collect_settings()` | Collect current GUI values |
| `_start_convert()` | Start conversion |
| `_poll_queue()` | Poll message queue (100 ms) |
| `_handle_msg(msg)` | Handle worker message |
| `_finish_convert()` | Finalize conversion |
| `_on_close()` | Clean shutdown |
| `_on_drop(event)` | Handle drag-and-drop |
| `_browse_input()` | Open input file dialog |
| `_browse_output()` | Open output file dialog |
| `_on_preset()` | Apply preset |

---

## 3. Memory Management

### 3.1. Temporary files

- Each launch creates a unique session directory: `%TEMP%/step2glb/<PID>/`.
- On non-ASCII paths, the input file is copied to the session directory.
- Intermediate tessellation results are written to `output.glb` inside the session directory.
- The session directory is deleted on exit.

### 3.2. Stale session cleanup

On startup, `%TEMP%/step2glb/` is scanned:
- Same PID → directory removed (leftover from crash).
- Dead PID → directory removed.

### 3.3. Buffer strategy

| Mode | Behavior |
|------|----------|
| `auto` | Disk temp file if >500 MB |
| `disk` | Always write temp file |
| `none` | Everything in RAM |
| `force` | Always disk, regardless of size |

---

## 4. Conversion Pipeline

### 4.1. STEP files

```
Input STEP → cascadio.step_to_glb() → GLB → [gzip] → Output file
```

### 4.2. IGES files

```
Input IGES → read to bytes → cascadio.load(file_type="iges") → GLB bytes → write → [gzip] → Output file
```

### 4.3. Gzip compression

```
GLB (binary) → gzip.open() → 1 MB chunks → GLB.GZ
```

Typical compression: 30–70% of original GLB size.

---

## 5. Inter-Process Communication (IPC)

### 5.1. Mechanism

`multiprocessing.Queue` passes dict messages from worker to GUI.

### 5.2. Thread safety

- `Queue` is thread-safe from the Python standard library.
- GUI polls via `after(100, ...)` — non-blocking.
- Empty queue exceptions are caught via `try/except`.

### 5.3. Worker termination

- On window close with active conversion: `proc.terminate()` + `proc.join(timeout=3)`.
- Workers are created with `daemon=True` — auto-terminated on main process exit.

---

## 6. Error Handling

| Situation | Behavior |
|-----------|----------|
| Invalid file extension | `messagebox.showerror` |
| File not found | `messagebox.showerror` |
| cascadio error | `error` message in log |
| Non-ASCII path | Auto-copy + log warning |
| Write error | Exception caught in worker, `error` sent |
| Conversion on close | Confirmation dialog → terminate |

---

## 7. Security

- No network usage — all operations are local.
- No secrets, keys, or tokens stored or transmitted.
- Temporary files are deleted on exit.
- File paths are not logged persistently.
- Code contains no API keys or private data.
