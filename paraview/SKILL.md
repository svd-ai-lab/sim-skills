---
name: paraview-sim
description: Use when post-processing and visualizing large-scale CFD/FEA simulation results via ParaView's paraview.simple Python API — loading .vtu/.vtk/.case/.foam/.cgns data, applying filters (Clip/Slice/Contour/Threshold/StreamTracer), batch rendering PNG screenshots via pvpython/pvbatch, and extracting quantitative metrics (IntegrateVariables, PlotOverLine, Calculator).
---

# paraview-sim

You are connected to **ParaView** via sim-cli.

ParaView is an open-source data visualization and analysis application
built on VTK, developed by Kitware / Sandia / LANL / LLNL. It is sim's
**heavyweight post-processor** for large-scale parallel visualization.

- Read 30+ file formats natively (.vtu, .vtk, .case, .foam, .cgns, .pvd, .exo, .stl, .xdmf)
- Apply filters: Clip, Slice, Contour, Threshold, StreamTracer, Calculator, IntegrateVariables
- Render PNG screenshots headlessly via OSMesa/EGL
- Extract quantitative metrics for acceptance validation
- Parallel processing via pvbatch + MPI

Scripts are Python using `paraview.simple` API. Executed via
`sim run script.py --solver paraview` (one-shot via pvpython).

---

## Identity

| Field | Value |
|---|---|
| Solver | ParaView (Kitware) |
| Execution mode | One-shot batch (`pvpython` / `pvbatch`) |
| Session type | None (Phase 1) |
| SDK | `paraview.simple` (bundled with ParaView binary or conda) |
| Script language | Python |
| Input formats | `.vtu`, `.vtk`, `.vtp`, `.vti`, `.vts`, `.pvd`, `.case`, `.foam`, `.cgns`, `.exo`, `.stl`, `.xdmf`, `.csv` |
| Output | JSON on stdout (last line), PNG screenshots, exported data files |

---

## Scope

**In scope:**
- Loading simulation results from any supported format
- Applying visualization filters (Clip, Slice, Contour, Threshold, StreamTracer)
- Computing derived quantities (Calculator, IntegrateVariables, PlotOverLine)
- Batch rendering screenshots (SaveScreenshot)
- Exporting filtered/transformed data (SaveData)
- Color mapping and transfer function configuration

**Out of scope:**
- Running solvers (ParaView is post-processing only)
- Interactive GUI sessions (use pvpython/pvbatch batch mode)
- Mesh generation (use Gmsh, ICEM, or solver-native meshers)
- pyvista operations (use pyvista-sim skill instead for lightweight VTK work)

---

## Hard constraints

1. **ParaView is NOT pip-installable.** Install via `conda install conda-forge::paraview`
   or download the binary from paraview.org. The `pvpython` executable must be on PATH
   or at a known install location.

2. **Use `paraview.simple` module exclusively.** All scripts must use the high-level
   `paraview.simple` API, not raw VTK calls. This ensures compatibility across versions.

3. **Always call `UpdatePipeline()` after reader/filter creation** before accessing data.
   Without it, the pipeline is lazy and data arrays may be empty.

4. **Headless rendering requires OSMesa or EGL.** On servers without a display, ParaView
   must be built with OSMesa (software) or EGL (GPU) support. The conda-forge build
   includes OSMesa by default.

5. **Never use `Interact()` in batch scripts.** It blocks indefinitely waiting for
   user input. Use `Render()` + `SaveScreenshot()` instead.

6. **JSON result on last stdout line.** All snippets must `print(json.dumps({...}))`
   as the final output for `driver.parse_output()` to extract.

7. **ParaView's Python is isolated.** pvpython ships its own Python interpreter.
   Don't assume pip packages are available. Use only stdlib + paraview + numpy (bundled).

---

## File index

### base/ — always relevant

| Path | Content |
|---|---|
| `base/reference/paraview_simple_api.md` | Core `paraview.simple` API: readers, sources, filters, rendering, writers |
| `base/reference/file_formats.md` | Supported file formats and their readers |
| `base/reference/rendering.md` | Headless rendering setup, camera control, color maps, screenshots |
| `base/reference/mcp_patterns.md` | Patterns from paraview_mcp (LLNL) for common operations |
| `base/snippets/01_smoke_test.py` | Minimal sphere render + JSON output |
| `base/snippets/02_load_and_stats.py` | Load data file, report array names and bounds |
| `base/snippets/03_contour_render.py` | Create iso-surface contour and render PNG |
| `base/snippets/04_slice_export.py` | Slice plane + export CSV data |
| `base/snippets/05_integrate_variables.py` | IntegrateVariables for surface/volume quantities |
| `base/known_issues.md` | Discovered failure modes and workarounds |

### base/workflows/

| Path | Content |
|---|---|
| `base/workflows/wavelet_filters/README.md` | Wavelet → 5 filters E2E evidence (2026-04-16, PV 5.4.1 Linux) |
| `base/workflows/wavelet_filters/e2e_summary.json` | 7/8 pass (rendering needs OSMesa) |

### sdk/ — version-specific notes

| Path | Content |
|---|---|
| `sdk/5_13/notes.md` | Python venv support, new readers, API changes |
| `sdk/5_4/notes.md` | Python 2.7, Threshold/SaveScreenshot API differences |

---

## Required protocol

### Step 0 — Version check

```bash
sim check paraview
```

Confirm ParaView is installed and version is known.

### Step 1 — Input validation (Category A/B/C)

| Input | Category | Action |
|---|---|---|
| Data file path | A | Must be provided by user |
| Variable to visualize | A | Must ask — do not guess field names |
| Acceptance criteria | A | Must ask — "outlet pressure within 5%" etc. |
| Color map | B | Default `viridis`, disclose |
| Screenshot resolution | B | Default `1920x1080`, disclose |
| Camera position | B | Default `ResetCamera()`, disclose |

### Step 2 — Load data

```python
from paraview.simple import *
reader = OpenDataFile("path/to/data.vtu")
UpdatePipeline()
```

Verify: `reader` is not None, data arrays exist.

### Step 3 — Apply filters and compute

Build the visualization pipeline. Always `UpdatePipeline()` after each filter.

### Step 4 — Render and export

```python
SaveScreenshot("output.png", magnification=2)
```

### Step 5 — Acceptance validation

Check computed quantities against user-specified criteria.
`exit_code == 0` alone is NOT sufficient.

---

## Layered content

- `sdk/5_13/` — ParaView 5.13 specific notes (Python venv, new readers)
- `solver/5_13/` — Version-specific rendering quirks
