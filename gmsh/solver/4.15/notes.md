# Gmsh 4.15 Notes

## Provenance

- Source: PyPI `gmsh` package (`pip install gmsh`)
- Installed version: 4.15.2
- Wheel: self-contained, includes both Python module and CLI wrapper
- Install path: `<venv>/bin/gmsh` (wrapper) + `<venv>/lib/python*/site-packages/gmsh.py`

## Capabilities verified on this build

| Feature | Status | Notes |
|---------|--------|-------|
| `SetFactory("OpenCASCADE")` | Verified | E2E sphere mesh |
| `Sphere / Box / Cylinder` | Verified | Primitives |
| `Physical Volume / Surface` | Verified | Tags exported |
| 3D tet meshing | Verified | 258 nodes, 1278 elems for r=1 sphere |
| MSH 2.2 export (`-format msh22`) | Verified | Wider compatibility |
| Python API (`import gmsh`) | Verified | Used in fixture + E2E |

## Default options in 4.15

- Mesh format: MSH 4.1 (override with `-format msh22`)
- 2D algorithm: Frontal-Delaunay (6)
- 3D algorithm: Delaunay (1)
- Element order: linear (1)

## Known limitations of 4.15 vs 4.13

- Minor field syntax deprecations in 4.12+
- Binary MSH 4 write path has edge cases with custom data

## Version detection

The driver runs `python -c "import gmsh; gmsh.initialize(); print(gmsh.option.getString('General.Version'))"`
and reads the version string from stdout.
