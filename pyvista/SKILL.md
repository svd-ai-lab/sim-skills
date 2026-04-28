---
name: pyvista-sim
description: Use when post-processing / visualizing simulation results — reading .vtu/.vtk/.msh outputs from CalculiX/Elmer/SU2/OpenFOAM, computing scalar stats (max, min, area, volume), extracting iso-surfaces, and generating headless PNG renders via the pyvista Python library.
---

# pyvista-sim

You are connected to **pyvista** via sim-cli.

pyvista is a Pythonic VTK wrapper (≈ the scriptable side of ParaView).
It's sim's **post-processor**:

- Read `.vtu` / `.vtk` / `.msh` / `.stl` natively
- Compute integrals (area, volume), scalar stats
- Filter / extract iso-surfaces, streamlines, threshold
- Render PNG screenshots headlessly (with X virtual framebuffer)

Same Python-subprocess mode as meshio / scikit-fem.

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/dataset_classes.md` | `PolyData`, `UnstructuredGrid`, `StructuredGrid`, `ImageData`. |
| `base/reference/filters.md` | extract_surface, threshold, contour, compute_cell_sizes. |
| `base/reference/rendering.md` | Headless rendering (`off_screen=True`), screenshot(), camera. |
| `base/snippets/01_sphere_stats.py` | Verified area/volume integration snippet. |
| `base/known_issues.md` | Double-counting surface on mixed-dim mesh; xvfb for rendering. |

## sdk/0.47/

- `sdk/0.47/notes.md` — pyvista 0.47 API notes.

---

## Hard constraints

1. **pyvista is post-processing, not solving.** Acceptance = geometric
   or field statistics (area within tolerance, max value, etc).
2. **Mixed-dimension meshes double-count surfaces.** A Gmsh `.msh` with
   both surface-triangles and volume-tets will produce `extract_surface`
   area ≈ 2× true. Filter to single-dimension cells before measurement.
3. **Rendering requires a display.** On headless Linux, set
   `pyvista.OFF_SCREEN = True` AND ensure `xvfb-run` is wrapping the
   Python invocation, OR use `pyvista.start_xvfb()` at script start.
4. **VTU vs VTK vs MSH read naturally**; for `.frd` (CalculiX) you need
   to convert via meshio → .vtu first.

---

## Required protocol

Agent gets a simulation output file path (from previous solver step).
Writes `.py` that reads the file via `pyvista.read`, computes the
acceptance quantities, optionally renders a PNG. Runs via
`sim run --solver pyvista`. Validates result JSON.
