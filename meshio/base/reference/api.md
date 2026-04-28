# meshio Python API

> Applies to: meshio 5.x

## Core classes

### `meshio.Mesh`

The in-memory mesh representation.

```python
import meshio
import numpy as np

mesh = meshio.Mesh(
    points=np.array([[0,0,0],[1,0,0],[0,1,0]], dtype=float),   # shape (N, 3)
    cells=[
        ("triangle", np.array([[0, 1, 2]])),                    # list of (type, conn)
    ],
    point_data={"temperature": np.array([1.0, 2.0, 3.0])},     # optional
    cell_data={"material_id": [np.array([1])]},                # per CellBlock
    field_data={"Wall": np.array([1, 2])},                     # tag name → (id, dim)
)
```

### `meshio.CellBlock`

Each entry of `mesh.cells` is a `CellBlock`:

```python
for block in mesh.cells:
    print(block.type, block.data.shape)
# → triangle (N_tri, 3)
#   tetra    (N_tet, 4)
```

## Read / Write

```python
# Auto-detect by extension
mesh = meshio.read("input.msh")
meshio.write("output.vtk", mesh)

# Explicit format
mesh = meshio.read("input.out", file_format="vtu")
meshio.write("output.bin", mesh, file_format="xdmf", compression="gzip")
```

## Filter / transform

```python
# Filter to specific cell types
tri_only = meshio.Mesh(
    points=mesh.points,
    cells=[(c.type, c.data) for c in mesh.cells if c.type == "triangle"],
)

# Re-number points (drop unused)
import numpy as np
used = np.unique(np.concatenate([c.data.flatten() for c in mesh.cells]))
remap = {old: new for new, old in enumerate(used)}
# ... apply remap to cells and points

# Transform coordinates
mesh.points *= 1e-3                           # mm → m
mesh.points[:, 2] += 0.5                      # shift z
```

## Common operations

### Count cells of each type
```python
counts = {c.type: len(c.data) for c in mesh.cells}
```

### Bounding box
```python
import numpy as np
pts = np.asarray(mesh.points)
bbox = {
    "min": pts.min(axis=0).tolist(),
    "max": pts.max(axis=0).tolist(),
}
```

### Extract surface from volume
```python
# Gmsh stores triangles (boundary) + tets (volume) in one mesh
tris = [c for c in mesh.cells if c.type == "triangle"]
tets = [c for c in mesh.cells if c.type == "tetra"]
volume_only = meshio.Mesh(mesh.points, cells=tets)
surface_only = meshio.Mesh(mesh.points, cells=tris)
```

### Preserve physical tags (Gmsh → anything)
```python
mesh = meshio.read("input.msh")
# Gmsh stores physical tags under mesh.cell_data["gmsh:physical"]
# When writing to .xdmf or .vtu, these become cell scalars automatically.
# When writing to .inp (Abaqus/CalculiX), they become *ELSET per tag.
meshio.write("output.xdmf", mesh)
```

## CLI equivalent

```bash
meshio convert input.msh output.vtk
meshio info mesh.vtu
meshio compress mesh.vtu              # gzip XML
meshio binary mesh.vtk                # legacy ASCII → binary
meshio ascii mesh.vtk                 # binary → ASCII
```

## Error handling

```python
try:
    mesh = meshio.read("mesh.msh")
except meshio.ReadError as e:
    print("parse failure:", e)
except FileNotFoundError:
    print("missing file")
```

## Gotchas

- `mesh.cells` is LIST of CellBlock (since 5.0); pre-5.0 code using
  `mesh.cells["triangle"]` is broken
- `meshio.write()` silently overwrites existing files — check first
- XDMF writes a sibling `.h5` with the same basename — both must be
  kept together
- Physical tag name is `"gmsh:physical"` (literal string) in cell_data
- Binary `.vtk` and `.vtu` are NOT the same — `.vtu` is XML (gzippable),
  `.vtk` legacy has its own binary format
