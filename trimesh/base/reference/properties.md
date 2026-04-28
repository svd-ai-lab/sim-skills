# Geometric properties

| Attribute | Type | Notes |
|---|---|---|
| `m.volume` | float | volume (only valid if watertight) |
| `m.area` | float | total surface area |
| `m.area_faces` | (n_faces,) array | per-face area |
| `m.bounds` | (2, 3) | min, max bbox corners |
| `m.extents` | (3,) | bbox edge lengths |
| `m.bounding_box` | Trimesh | the bbox itself |
| `m.bounding_box_oriented` | Trimesh | minimum-volume oriented bbox |
| `m.bounding_sphere` | Trimesh | circumscribed sphere |
| `m.center_mass` | (3,) | centroid (only valid if watertight) |
| `m.centroid` | (3,) | mesh centroid (always defined) |
| `m.moment_inertia` | (3, 3) | inertia tensor about COM |
| `m.principal_inertia_components` | (3,) | eigenvalues of inertia |
| `m.convex_hull` | Trimesh | convex hull as a new mesh |
| `m.vertices` | (n_v, 3) | vertex coords |
| `m.faces` | (n_f, 3) | triangle vertex indices |
| `m.face_normals` | (n_f, 3) | per-face normal |
| `m.vertex_normals` | (n_v, 3) | per-vertex normal (averaged) |

## Topology checks

| Attribute | Bool | Meaning |
|---|---|---|
| `is_watertight` | True/False | closed manifold (volume valid) |
| `is_winding_consistent` | True/False | normals all out (or all in) |
| `is_volume` | True/False | shorthand for the above two |
| `is_convex` | True/False | every face on the convex hull |
| `is_empty` | True/False | zero faces |

## Cross-section / slicing

```python
slice_2d = m.section(plane_origin=[0, 0, 0.5], plane_normal=[0, 0, 1])
slice_2d.show()
```
