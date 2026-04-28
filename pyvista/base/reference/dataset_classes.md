# pyvista Dataset Classes

> Applies to: pyvista 0.47

## Dataset hierarchy

```
DataSet (abstract)
├── PointSet
│   ├── PolyData          — surface meshes (triangles + polylines + vertices)
│   ├── UnstructuredGrid  — arbitrary cells (tets, hexes, mixed)
│   └── StructuredGrid    — curvilinear structured (logical i,j,k)
└── ImageData             — regular Cartesian grid (voxels)
```

## Creating common shapes

```python
import pyvista as pv

sphere = pv.Sphere(radius=1.0, theta_resolution=20, phi_resolution=20)
box    = pv.Cube(x_length=1, y_length=1, z_length=1)
plane  = pv.Plane(direction=(0, 0, 1), i_size=1, j_size=1)
line   = pv.Line(pointa=(0,0,0), pointb=(1,0,0))
cyl    = pv.Cylinder(radius=0.5, height=2.0)
```

All return `PolyData` — surface meshes.

## Reading from files

```python
# Auto-detect by extension
grid = pv.read("mesh.vtu")            # → UnstructuredGrid
grid = pv.read("surface.stl")         # → PolyData

# With explicit reader
reader = pv.XMLUnstructuredGridReader("mesh.vtu")
grid = reader.read()
```

Supported extensions: `.vtu`, `.vtk`, `.vtp`, `.stl`, `.ply`, `.obj`,
`.case` (EnSight), `.cgns`, `.dat` (Tecplot ASCII).

## Common attributes

```python
grid.n_points                    # vertex count
grid.n_cells                     # cell count
grid.bounds                      # (xmin, xmax, ymin, ymax, zmin, zmax)
grid.points                      # (N, 3) numpy array
grid.center                      # centroid
grid.extent                      # size on each axis

# Per-cell / per-point arrays
grid.point_data["Temperature"]   # numpy array, len == n_points
grid.cell_data["Pressure"]       # numpy array, len == n_cells
grid.array_names                 # list of all arrays
```

## Cell types (VTK codes)

| pyvista | VTK code | Points | Topology |
|---------|----------|--------|----------|
| `VERTEX` | 1 | 1 | — |
| `LINE` | 3 | 2 | line |
| `TRIANGLE` | 5 | 3 | tri |
| `QUAD` | 9 | 4 | quad |
| `TETRA` | 10 | 4 | tet |
| `HEXAHEDRON` | 12 | 8 | hex |
| `WEDGE` | 13 | 6 | prism |
| `PYRAMID` | 14 | 5 | pyramid |

## Common pattern: isolate cell type

```python
# Keep only tets from a mixed mesh
tets_mask = grid.celltypes == pv.CellType.TETRA
tets = grid.extract_cells(tets_mask)
```

## Gotchas

- `grid.points` is a numpy `.writeable = False` view — use `.copy()` to
  modify
- `point_data` and `cell_data` are dict-like but enforce array length
- Mixed-dimension meshes (surface tris + volume tets in one file) cause
  `extract_surface` to double-count faces — filter first
