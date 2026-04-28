# Gmsh Python API

> Applies to: Gmsh 4.x (pip package)

## Skeleton

```python
import gmsh
import sys

gmsh.initialize(sys.argv)        # pass argv for CLI flag parsing
gmsh.model.add("my_model")

# ... build geometry ...

gmsh.model.occ.synchronize()      # MANDATORY after OCC create/boolean
gmsh.model.mesh.generate(3)       # 1D, 2D, or 3D

gmsh.write("out.msh")             # format inferred from extension
gmsh.finalize()
```

## Geometry (OpenCASCADE)

```python
occ = gmsh.model.occ
sphere = occ.addSphere(0, 0, 0, 1.0)               # returns tag
box    = occ.addBox(0, 0, 0, 1, 1, 1)
cyl    = occ.addCylinder(0, 0, 0, 0, 0, 1, 0.5)

# Booleans return (new_entities, mapping)
out, _ = occ.fuse([(3, sphere)], [(3, box)])
out, _ = occ.cut ([(3, sphere)], [(3, box)])
out, _ = occ.intersect([(3, sphere)], [(3, box)])

occ.synchronize()                 # REQUIRED before .mesh / tag queries
```

## Physical groups

```python
# Add by dim+tags → returns physical group tag
gmsh.model.addPhysicalGroup(3, [sphere], tag=1, name="ball")
gmsh.model.addPhysicalGroup(2, [1, 2, 3], tag=2, name="walls")

# Or set name separately
pg = gmsh.model.addPhysicalGroup(3, [sphere])
gmsh.model.setPhysicalName(3, pg, "ball")
```

## Mesh generation

```python
gmsh.model.mesh.generate(3)               # dimension
gmsh.model.mesh.optimize("Netgen")        # quality optimization
gmsh.model.mesh.setOrder(2)               # high-order elements
gmsh.model.mesh.recombine()               # all-quad / all-hex via recombine
```

## Mesh size

```python
gmsh.option.setNumber("Mesh.MeshSizeMax", 0.3)
gmsh.option.setNumber("Mesh.MeshSizeMin", 0.05)

# Distance-threshold field combo
gmsh.model.mesh.field.add("Distance", 1)
gmsh.model.mesh.field.setNumbers(1, "PointsList", [1, 2])

gmsh.model.mesh.field.add("Threshold", 2)
gmsh.model.mesh.field.setNumber(2, "InField", 1)
gmsh.model.mesh.field.setNumber(2, "SizeMin", 0.02)
gmsh.model.mesh.field.setNumber(2, "SizeMax", 0.2)
gmsh.model.mesh.field.setNumber(2, "DistMin", 0.1)
gmsh.model.mesh.field.setNumber(2, "DistMax", 1.0)

gmsh.model.mesh.field.setAsBackgroundMesh(2)
```

## Query entities after geometry

```python
# All 3D entities (volumes)
vols = gmsh.model.getEntities(3)      # [(dim, tag), ...]

# Bounding box query
inside = gmsh.model.getEntitiesInBoundingBox(
    xmin, ymin, zmin, xmax, ymax, zmax, dim=2
)
```

## CAD import

```python
gmsh.model.occ.importShapes("part.step")   # STEP, IGES, BREP
gmsh.model.occ.importShapes("part.stl")    # STL (discrete)
gmsh.model.occ.synchronize()
```

## Writing meshes

```python
gmsh.write("out.msh")           # inferred MSH 4.1
gmsh.write("out.msh22")         # inferred MSH 2.2
gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
gmsh.write("out.msh")           # now MSH 2.2
```

## Common pattern for sim workflow

```python
import gmsh, sys, json
gmsh.initialize()
gmsh.model.add("sphere")
gmsh.model.occ.addSphere(0, 0, 0, 1.0)
gmsh.model.occ.synchronize()
gmsh.option.setNumber("Mesh.MeshSizeMax", 0.3)
gmsh.model.mesh.generate(3)
gmsh.write("sphere.msh")

n_nodes = len(gmsh.model.mesh.getNodes()[0])
n_elems = sum(len(t) for t in gmsh.model.mesh.getElements()[1])
print(json.dumps({"ok": True, "nodes": n_nodes, "elements": n_elems}))
gmsh.finalize()
```

## Gotchas

- `gmsh.initialize()` MUST be matched by `gmsh.finalize()` or the next
  run will warn / misbehave
- `occ.synchronize()` is NOT automatic — forgetting it causes empty
  entity queries or missed boolean results
- `generate(1)` / `(2)` / `(3)` sequentially — only the highest dim is
  typically needed but intermediate meshes exist
- Field numbering: each field is added with an integer ID you manage
- In Python API, entity pairs are `(dim, tag)` tuples
