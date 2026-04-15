# meshio 5.x Notes

## Provenance

- Source: PyPI `meshio` package, installed with `[all]` extras
- Version: 5.3.5
- Optional deps (via `[all]`): h5py (XDMF), netCDF4 (CGNS), rich (CLI output)

## Capabilities verified

| Feature | Status | Notes |
|---------|--------|-------|
| Read .msh (Gmsh v2) | Verified | 258 points, 1278 cells |
| Write .vtk | Verified | Round-trip preserves points |
| `meshio.Mesh` API | Verified | CellBlock iteration |
| CLI `meshio convert` | Verified | Installed at `<venv>/bin/meshio` |
| CLI `meshio info` | Verified | Summary output |

## API stability

5.x has been stable since 2021. Breaking change from 4.x:
- `mesh.cells` is list[CellBlock] (was dict)
- `mesh.cell_data` is dict[str, list[array]] (unchanged conceptually)

## Version detection

Driver runs `python -c "import meshio; print(meshio.__version__)"` and
gets `5.3.5`. Normalized to short form `5.3`.
