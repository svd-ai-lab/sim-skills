# Known Issues — pyvista Driver

## Mixed-dim mesh doubles surface area

**Discovered**: 2026-04-14
**Status**: Handled in snippet
**Description**: A Gmsh `.msh` exported with both `Physical Surface` and
`Physical Volume` contains boundary triangles AND volume tetrahedra.
`grid.extract_surface()` on this mesh counts each external face TWICE
(once from the triangle cells, once as a tet face).
**Fix**: filter to single dimension before measurement:
```python
tet_only = meshio.Mesh(points=mesh.points,
                      cells=[(c.type, c.data) for c in mesh.cells
                             if c.type == "tetra"])
```

## Headless rendering needs xvfb

**Status**: User-input driven
**Description**: `pyvista.Plotter().screenshot()` requires an X server.
On headless Linux:
- `pv.start_xvfb()` at script start, OR
- wrap script with `xvfb-run -a python script.py`

Without this, plotter.screenshot fails with "Could not open display".

## `compute_cell_sizes` naming

**Status**: API quirk
**Description**: `compute_cell_sizes()` adds **`"Volume"` (capitalized)**
as the cell_data key — not `volume`. Case-sensitive.

## .frd (CalculiX) not natively readable

**Status**: Bridge via meshio
**Description**: pyvista has no .frd reader. To post-process CalculiX
output, go via meshio: `meshio convert case.frd case.vtu` first.
Actually meshio doesn't read .frd either — use `ccx2paraview` CLI tool
or a custom parser. As of 2026-04, easiest workflow is to request
`.vtu` output directly from the solver (Elmer does this natively; for
CalculiX, use the ccx2paraview conversion utility).

## `mesh.area` on non-closed surface is misleading

**Status**: Expected
**Description**: `PolyData.area` sums the areas of all triangles. For an
open mesh (e.g. a plate with one face), it's just the plate area. For a
closed mesh (sphere), it's the full surface area. No volume meaning.

## Large datasets + OFF_SCREEN = memory spike

**Status**: Known behavior
**Description**: Rendering large meshes off-screen copies geometry into
VTK's render buffer. For > 10M cells, either downsample first or use
a streaming workflow.
