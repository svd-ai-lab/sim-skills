# pyvista 0.47 Notes

## Provenance

- Source: PyPI `pyvista`
- Version: 0.47.3
- Dependencies installed: `vtk`, `numpy`, `scooby`, `matplotlib`

## Capabilities verified

| Feature | Status | Notes |
|---------|--------|-------|
| `pv.read(.vtu)` | Verified | Gmsh → meshio → pyvista E2E |
| `extract_surface` | Verified | For tet-only meshes |
| `compute_cell_sizes(volume=True)` | Verified | Tet volume sum matches analytical |
| `PolyData.area` | Verified | Surface area matches 4π |
| `n_points`, `n_cells`, `bounds` | Verified | Basic introspection |

## API notes for 0.47

- `extract_surface` has a new `algorithm=` kwarg (deprecation warning
  if unset). Safe to ignore for simple cases.
- `Plotter.show()` on headless defaults to calling `start_xvfb()` if
  OFF_SCREEN=True is set.
- New `pv.CellType` enum for cell-type comparisons in 0.47+.

## Version detection

`python -c "import pyvista; print(pyvista.__version__)"` → `0.47.3`,
normalized short form `0.47`.
