# Trimesh 4.x Notes

## Provenance

- Source: PyPI `trimesh`
- Verified version: 4.4.1
- Pure Python + NumPy/SciPy + optional accelerators

## Capabilities verified

| Feature | Status | Notes |
|---------|--------|-------|
| `trimesh.creation.box(extents=...)` | Verified | exact V/A |
| `trimesh.creation.icosphere(subdivisions, radius)` | Verified | <0.5% err |
| `m.volume`, `m.area` | Verified | float (np.float64) |
| `m.is_watertight` | Verified | bool (np.bool_) |
| `m.bounds`, `m.extents` | Verified | numpy arrays |

## Box + sphere benchmark

Box(2,3,4): V=24.0, A=52.0 — exact.
Sphere(r=1, subdiv=4): V=4.180 (theory 4.189, 0.2% err); A=12.55 (theory 12.57, 0.1% err); watertight=True.

## Version detection

```bash
python3 -c "import trimesh; print(trimesh.__version__)"
```
returns `4.4.1`. Driver normalizes to `4.4`.

## Optional acceleration packages

For full features, also install:
```bash
pip install rtree shapely mapbox-earcut manifold3d
```
- `rtree` — fast spatial indexing for ray casting
- `shapely` — 2D path / cross-section ops
- `mapbox-earcut` — polygon triangulation
- `manifold3d` — boolean (union/diff/intersection)
