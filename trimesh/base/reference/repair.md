# Mesh repair

```python
import trimesh

m = trimesh.load('broken.stl')
print(m.is_watertight)      # False — needs work

# 1. Merge near-coincident vertices
m.merge_vertices()

# 2. Fix face winding (consistent normals)
trimesh.repair.fix_winding(m)
trimesh.repair.fix_normals(m)

# 3. Fill small holes
m.fill_holes()

# 4. Remove duplicate faces / unreferenced vertices
m.remove_duplicate_faces()
m.remove_unreferenced_vertices()

# 5. Verify
print(m.is_watertight, m.is_winding_consistent)

# Save the cleaned-up mesh
m.export('repaired.stl')
```

## Specialized repair from `trimesh.repair`

| Function | Purpose |
|---|---|
| `fix_normals(m)` | flip face normals to point outward |
| `fix_winding(m)` | reorder triangle vertices for consistent winding |
| `fix_inversion(m)` | flip faces with inverted normals |
| `fill_holes(m)` | close small openings (planar contour) |
| `broken_faces(m)` | return indices of degenerate faces |
| `stitch(m)` | merge near-coincident edges |

## When repair fails

- For severely broken meshes, route through PyMesh or Open3D's reconstruction.
- For point-cloud → mesh, use Trimesh's `trimesh.points.PointCloud(...).convex_hull`
  or scikit-image marching cubes (`measure.marching_cubes`).
