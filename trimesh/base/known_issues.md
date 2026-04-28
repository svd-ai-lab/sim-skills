# Known Issues — Trimesh Driver

## numpy bool / float not JSON-serializable

**Status**: Common gotcha
**Description**: `m.is_watertight` returns `numpy.bool_`, `m.volume`
returns `numpy.float64`. Wrap with `bool(...)` / `float(...)` before
`json.dumps`, or use `default=str`.

## Volume valid only for watertight meshes

**Status**: Math
**Description**: `m.volume` for non-watertight meshes returns a
nonsense number (signed sum of tetrahedra). Always check
`m.is_watertight` first.

## Boolean ops need a backend

**Status**: Soft dependency
**Description**: `m.intersection(...)` raises `ImportError` if no
backend is installed. For pure pip:
```bash
pip install manifold3d
```

## Non-deterministic surface sampling

**Status**: Convention
**Description**: `trimesh.sample.sample_surface(m, n)` uses NumPy RNG.
Seed via `np.random.seed(42)` for reproducibility.

## Heavy import time

**Status**: Performance
**Description**: `import trimesh` ~0.5-1 s cold. The library auto-imports
many optional deps (rtree, embree, mapbox-earcut, scikit-image) and
gracefully degrades if missing.

## Unit conventions

**Status**: User responsibility
**Description**: Trimesh has no built-in units. Treat coordinates as
millimeters (STL convention) or meters (CAD convention) consistently.
`m.units = 'mm'` is just a tag; conversion is `m.apply_scale(1e-3)`.

## Disk export: text vs binary STL

**Status**: API
**Description**: `m.export('out.stl')` defaults to binary. For ASCII
STL: `m.export('out.stl', file_type='stl_ascii')`.
