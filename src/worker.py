"""Фоновый процесс конвертации STEP/IGES в GLB.

Background conversion worker process for STEP/IGES to GLB.
"""

import gzip
import multiprocessing
import os
import shutil
import time

from .config import GZIP_BUFFER_SIZE
from .utils import has_non_ascii


def _worker(
    q: multiprocessing.Queue,
    session_dir: str,
    inp: str,
    out: str,
    tol_lin: float,
    tol_ang: float,
    tol_rel: bool,
    merge: bool,
    parallel: bool,
    file_type: str,
    compress: bool,
) -> None:
    """Основная функция конвертации, выполняемая в дочернем процессе.

    Main conversion function executed inside a child (multiprocessing) process.
    Communicates with the GUI via the *q* (Queue) by sending dict messages.

    Supported message types:
        log    — строка лога / log line
        status — текущий статус / current status
        tess_done — результат tessellation
        done   — конвертация завершена / conversion finished
        error  — ошибка / error occurred
    """

    def emit(msg: dict) -> None:
        """Отправляет сообщение в GUI через очередь / Send a message to the GUI."""
        q.put(msg)

    try:
        src_name = os.path.basename(inp)
        tmp_inp = os.path.join(session_dir, "input" + os.path.splitext(src_name)[1])
        tmp_out = os.path.join(session_dir, "output.glb")

        # --- Начало лога / Start log ---
        emit({"type": "log", "text": f"Input: {inp}", "tag": "hi"})
        emit({"type": "log", "text": f"Output: {out}", "tag": "info"})
        emit({"type": "log", "text": f"Format: {file_type.upper()}", "tag": "info"})
        emit({
            "type": "log",
            "text": (
                f"Settings: lin={tol_lin}, ang={tol_ang}, "
                f"relative={tol_rel}, merge={merge}, parallel={parallel}, "
                f"compress={compress}"
            ),
            "tag": "dim",
        })

        # --- Копирование при наличии non-ASCII в путях ---
        # Copy to temp if the path contains non-ASCII characters.
        # cascadio cannot handle Cyrillic/unicode paths.
        if has_non_ascii(inp) or has_non_ascii(out):
            emit({
                "type": "log",
                "text": (
                    "Path contains non-ASCII characters (e.g. Cyrillic). "
                    "cascadio cannot handle such paths directly. "
                    "Using temp folder."
                ),
                "tag": "warn",
            })
            t_copy = time.time()
            shutil.copy2(inp, tmp_inp)
            dt_copy = time.time() - t_copy
            size_mb = os.path.getsize(tmp_inp) / GZIP_BUFFER_SIZE
            emit({
                "type": "log",
                "text": f"Copied to temp: {tmp_inp} ({size_mb:.1f} MB, {dt_copy:.1f}s)",
                "tag": "info",
            })
            emit({"type": "status", "text": f"Loaded ({size_mb:.1f} MB)"})
            use_temp = True
        else:
            tmp_inp = inp
            size_mb = os.path.getsize(inp) / GZIP_BUFFER_SIZE
            emit({
                "type": "log",
                "text": f"File: {inp} ({size_mb:.1f} MB)",
                "tag": "info",
            })
            emit({"type": "status", "text": f"Loaded ({size_mb:.1f} MB)"})
            use_temp = False

        # Импорт cascadio внутри воркера, чтобы не нагружать GUI-поток.
        # Import cascadio inside the worker to avoid loading heavy libs in the GUI thread.
        import cascadio

        emit({"type": "log", "text": f"cascadio {cascadio.__version__}", "tag": "dim"})

        final_out = tmp_out if use_temp else out

        emit({"type": "status", "text": "Tessellating..."})
        t0 = time.time()

        # --- Конвертация IGES / IGES conversion ---
        if file_type == "iges":
            emit({"type": "status", "text": f"Reading IGES ({size_mb:.0f} MB)..."})
            emit({"type": "log", "text": "Reading IGES file into memory...", "tag": "info"})

            with open(tmp_inp, "rb") as fh:
                data = fh.read()

            emit({
                "type": "log",
                "text": f"IGES data: {len(data) / GZIP_BUFFER_SIZE:.1f} MB loaded",
                "tag": "info",
            })
            emit({"type": "status", "text": f"Tessellating ({size_mb:.0f} MB)..."})
            emit({
                "type": "log",
                "text": (
                    f"Calling cascadio.load(file_type=iges, "
                    f"lin={tol_lin}, ang={tol_ang})..."
                ),
                "tag": "info",
            })

            glb_bytes = cascadio.load(
                data,
                file_type="iges",
                tol_linear=tol_lin,
                tol_angular=tol_ang,
                tol_relative=tol_rel,
                merge_primitives=merge,
                use_parallel=parallel,
            )

            if not glb_bytes:
                raise RuntimeError("cascadio IGES conversion failed")

            emit({
                "type": "log",
                "text": f"GLB output: {len(glb_bytes) / GZIP_BUFFER_SIZE:.1f} MB",
                "tag": "ok",
            })

            with open(final_out, "wb") as fh:
                fh.write(glb_bytes)

        # --- Конвертация STEP / STEP conversion ---
        else:
            emit({"type": "status", "text": f"Reading STEP ({size_mb:.0f} MB)..."})
            emit({
                "type": "log",
                "text": (
                    f"Calling cascadio.step_to_glb(lin={tol_lin}, "
                    f"ang={tol_ang})..."
                ),
                "tag": "info",
            })

            cascadio.step_to_glb(
                tmp_inp,
                final_out,
                tol_linear=tol_lin,
                tol_angular=tol_ang,
                tol_relative=tol_rel,
                merge_primitives=merge,
                use_parallel=parallel,
            )

            glb_size = os.path.getsize(final_out) / GZIP_BUFFER_SIZE
            emit({"type": "log", "text": f"GLB output: {glb_size:.1f} MB", "tag": "ok"})

        # --- Завершение tessellation / Tessellation complete ---
        dt = time.time() - t0
        emit({"type": "log", "text": f"Tessellation complete: {dt:.1f}s", "tag": "ok"})
        raw_mb = os.path.getsize(final_out) / GZIP_BUFFER_SIZE
        emit({"type": "tess_done", "time": dt, "size": os.path.getsize(final_out)})

        # --- Сжатие gzip (опционально) / Gzip compression (optional) ---
        if compress:
            emit({"type": "status", "text": "Compressing..."})
            emit({"type": "log", "text": "Compressing with gzip...", "tag": "info"})
            t_gz = time.time()

            gz_path = out + ".gz"
            with open(final_out, "rb") as fi, gzip.open(gz_path, "wb") as fo:
                while True:
                    chunk = fi.read(GZIP_BUFFER_SIZE)
                    if not chunk:
                        break
                    fo.write(chunk)

            out = gz_path
            c_mb = os.path.getsize(out) / GZIP_BUFFER_SIZE
            dt_gz = time.time() - t_gz
            ratio = c_mb / raw_mb * 100 if raw_mb else 0

            emit({
                "type": "log",
                "text": (
                    f"Compressed: {raw_mb:.1f} MB -> {c_mb:.1f} MB "
                    f"({ratio:.0f}%, {dt_gz:.1f}s)"
                ),
                "tag": "ok",
            })
            emit({
                "type": "done",
                "path": out,
                "time": time.time() - t0,
                "raw_mb": raw_mb,
                "comp_mb": c_mb,
            })
        else:
            if use_temp:
                os.replace(final_out, out)
                emit({"type": "log", "text": f"Moved to: {out}", "tag": "info"})
            emit({"type": "done", "path": out, "time": dt})

    except Exception as exc:
        emit({"type": "error", "text": str(exc)})
