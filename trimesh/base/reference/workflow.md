# Trimesh workflow

```python
import trimesh

# 1. Load (auto-detect format from extension)
m = trimesh.load('part.stl')             # STL / OBJ / PLY / 3MF / GLB
# or generate:
m = trimesh.creation.box(extents=[2, 3, 4])
m = trimesh.creation.icosphere(subdivisions=4, radius=1.0)
m = trimesh.creation.cylinder(radius=0.5, height=2)

# 2. Inspect
print(m.is_watertight, m.is_winding_consistent, m.is_volume)
print(m.bounds)              # (2, 3) array: min, max
print(m.extents)             # (3,) bbox sizes

# 3. Repair (in place) if needed
if not m.is_watertight:
    trimesh.repair.fix_normals(m)
    m.fill_holes()
    m.merge_vertices()

# 4. Analyze
V = m.volume                 # float (only valid if watertight)
A = m.area                   # surface area
I = m.moment_inertia         # 3x3 inertia tensor
com = m.center_mass          # (3,)
hull = m.convex_hull         # new Trimesh

# 5. Export
m.export('out.stl')
m.export('out.ply')
m.export('out.glb')
```

## Always emit JSON

```python
import json
print(json.dumps({
    "ok": bool(m.is_watertight),
    "volume": float(m.volume),
    "area":   float(m.area),
}))
```
