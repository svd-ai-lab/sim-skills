# Known Issues — meshio Driver

## Cells API changed in 5.0

**Status**: By design
**Description**: Pre-5.0 code used `mesh.cells["triangle"]` dict access.
meshio 5.0+ returns a list of `CellBlock` objects — use
`[c for c in mesh.cells if c.type == "triangle"]`. Upgrading legacy
scripts usually needs this one change.

## Physical group tag name is literal

**Status**: User-input driven
**Description**: Gmsh physical tags land in `mesh.cell_data["gmsh:physical"]`
— the string includes the colon. Don't strip it; solvers that understand
meshio preserve this key across conversions.

## XDMF needs h5py

**Status**: Install-time
**Description**: Reading/writing `.xdmf` requires the `h5py` package.
`pip install meshio[all]` pulls it in; bare `pip install meshio` doesn't.
Our venv has it via `[all]`.

## VTK legacy is NOT the same as VTU

**Status**: Format naming
**Description**: `.vtk` = legacy VTK (text or binary, single file).
`.vtu` = modern VTK XML unstructured (XML, single file, optional gzip).
They are NOT interchangeable — different parsers. Use `.vtu` for
ParaView; `.vtk` for compatibility with older tools.

## `meshio.convert()` CLI vs library
**Status**: Reference
**Description**: The CLI `meshio convert` exists but when scripting
from sim, use `meshio.read(...); meshio.write(...)` in Python for
parseable output (JSON result). CLI is for ad-hoc shell use.

## No solver role

**Status**: By design
**Description**: meshio is a mesh-format bridge, not a physics solver.
"Acceptance" means topology preserved (points, cells, bbox), NOT
physical validity. For physics validation, pair meshio with an actual
solver driver (CalculiX, Elmer, SU2).
