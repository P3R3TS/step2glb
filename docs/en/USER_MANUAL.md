# User Manual

## step2glb — STEP/IGES to GLB Converter

---

**Document version:** 1.0  
**Date:** September 2026  
**Applicable standards:** GOST 19.201-78, GOST 19.701-90  

---

## 1. General Information

### 1.1. Purpose

**step2glb** converts 3D models from STEP and IGES formats to GLB (glTF Binary). The application provides a GUI with drag-and-drop support, tessellation quality control, and optional compression.

### 1.2. Installation

#### Running the prebuilt executable

1. Place `step2glb.exe`, `step2glb.bat`, and `step2glb.ini` in the same folder.
2. Double-click `step2glb.exe` or `step2glb.bat`.

#### Running from source

```bash
pip install -r requirements.txt
python main.py
```

### 1.3. Compatibility

- Windows 7, 8, 10, 11
- Linux (GTK-based desktops)
- macOS 10.14+

---

## 2. Interface Overview

### 2.1. Window layout

```
+-----------------------------------------------+
|  Input file                                   |
|  [File path]                       [Browse…]  |
+-----------------------------------------------+
|  Drag & drop STEP / IGES file here            |
+-----------------------------------------------+
|  Settings                                     |
|  Preset: ○draft ○normal ○high ○ultra          |
|  Lin: [___]  Ang: [___]                       |
|  □Relative  ☑Merge  ☑Parallel                 |
|  Buffer: [auto ▼]  □Gzip                      |
+-----------------------------------------------+
|  Output file                                  |
|  [File path]                       [Browse…]  |
+-----------------------------------------------+
|  ▶  Convert                                   |
+-----------------------------------------------+
|  Progress                                     |
|  [============================] 100%          |
|  Status: Completed in 12.3s                   |
|  +------------------------------------------+ |
|  | Log console (dark theme)                 | |
|  +------------------------------------------+ |
+-----------------------------------------------+
```

### 2.2. Selecting an input file

**Method 1 — Browse button:**
1. Click **Browse…** in the "Input file" section.
2. Select a STEP or IGES file in the file dialog.
3. Click "Open".

**Method 2 — Drag and drop:**
1. Drag a STEP/IGES file from the file explorer into the drop zone.
2. The file path will appear in the input field automatically.

**Method 3 — Manual path:**
The input field is read-only. Use Browse or drag-and-drop instead.

### 2.3. Settings

#### Presets

Quick selection of pre-configured parameter combinations:

| Preset | Description | Speed | Quality |
|--------|-------------|:-----:|:-------:|
| **draft** | Fast, coarse mesh (preview) | ★★★★★ | ★ |
| **normal** | Balanced | ★★★ | ★★★ |
| **high** | Detailed, slower | ★★ | ★★★★ |
| **ultra** | Maximum quality, very slow | ★ | ★★★★★ |

Selecting a preset automatically fills the **Lin** and **Ang** fields.

#### Linear Deflection (Lin)

Maximum distance between the real surface and the triangle mesh.

- Lower value → more triangles → finer detail
- Range: 0.0001 – 10.0
- Examples: `0.001` (ultra), `0.01` (high), `0.1` (normal), `1.0` (draft)

#### Angular Deflection (Ang)

Maximum angle (in radians) between normals of adjacent triangles.

- Lower value → smoother curves
- Range: 0.01 – 10.0
- Examples: `0.1` (ultra), `0.2` (high), `0.5` (normal), `1.0` (draft)

#### Checkboxes

| Checkbox | ON | OFF |
|----------|-----|-----|
| **Relative** | Linear deflection = percentage of edge length | Absolute distance in model units |
| **Merge** | All triangle faces → single mesh (smaller file) | Each face = separate primitive (more glTF nodes) |
| **Parallel** | All CPU cores used (faster) | Single-threaded (less RAM) |

#### Buffer Strategy

Memory management for large files:

| Mode | Description |
|------|-------------|
| **auto** | Disk buffer when file >500 MB |
| **disk** | Always write temp file to reduce RAM |
| **none** | Keep everything in RAM |
| **force** | Always use disk, even for small files |

#### Gzip Compression

When enabled, the output is saved as `.glb.gz`. Typically 30–70% smaller. Most 3D viewers support `.glb.gz`.

### 2.4. Selecting an output file

1. Click **Browse…** in the "Output file" section.
2. Specify the path and filename with `.glb` extension.
3. By default the filename matches the input file with `.glb` extension.

### 2.5. Converting

1. Ensure both input and output files are selected.
2. Adjust tessellation settings if needed.
3. Click **▶ Convert**.
4. Monitor progress in the progress bar and log console.
5. Completion summary appears in the log.

### 2.6. Log Console

The dark console at the bottom displays detailed conversion information:

| Color | Tag | Description |
|-------|-----|-------------|
| White | `info` | Informational messages |
| Blue | `hi` | Important messages (file path) |
| Gray | `dim` | Supplementary information |
| Green | `ok` | Successful operation |
| Yellow | `warn` | Warnings |
| Red | `err` | Errors |

---

## 3. Configuration Files

### 3.1. step2glb.ini

Settings are automatically saved to `step2glb.ini` in the launch directory:

```ini
[main]
preset = normal
lin = 0.1
ang = 0.5
relative = false
merge = true
parallel = true
buffer = auto
compress = true
```

Settings are restored on the next launch.

---

## 4. Troubleshooting

### 4.1. "Cannot open .xyz"

Only `.stp`, `.step`, `.igs`, `.iges` extensions are supported. Ensure the file has the correct extension.

### 4.2. No drag-and-drop

`tkinterdnd2` is not installed:

```bash
pip install tkinterdnd2
```

Or use the **Browse** button instead.

### 4.3. Cyrillic / non-ASCII paths

cascadio cannot handle non-ASCII paths. The program automatically copies the file to a temp folder. A warning appears in the log.

### 4.4. Out of memory

For large files (>500 MB), set the buffer strategy to **disk** or **force**.

### 4.5. Conversion is very slow

Use the **draft** preset for quick checks. For final export, choose **normal** or **high**.
