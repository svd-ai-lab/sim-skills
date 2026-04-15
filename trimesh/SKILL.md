---
name: trimesh-sim
description: Use when driving Trimesh (pure-Python triangular-mesh processing library) via Python scripts — load STL/OBJ/PLY/3MF/GLB, compute volume / area / inertia / convex hull / signed distance / ray casts, repair non-watertight meshes, boolean ops, sample points — through sim runtime one-shot execution.
---

# trimesh-sim

You are connected to **Trimesh** via sim-cli.

Trimesh is the standard Python library for triangular-mesh manipulation
(Dawson-Haggerty et al.). Pure Python on top of NumPy/SciPy with optional
acceleration (rtree, embree, mapbox-earcut, scikit-image). Pip-installable
(`pip install trimesh`).

Scripts are plain `.py`:

```python
import trimesh
m = trimesh.load('part.stl')
print(m.volume, m.area, m.is_watertight)
if not m.is_watertight:
    trimesh.repair.fix_normals(m)
    m.fill_holes()
m.export('repaired.stl')
```

Same subprocess driver mode as PyBaMM / PyMFEM / SfePy.

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/workflow.md` | Load → inspect → repair → analyze → export. |
| `base/reference/properties.md` | Volume, area, inertia, COM, convex hull, bounds. |
| `base/reference/repair.md` | fill_holes, fix_normals, fix_winding, merge_vertices. |
| `base/reference/operations.md` | Boolean (union/diff/intersection), section, slicing, ray casts. |
| `base/snippets/01_props.py` | Verified box + sphere volume/area E2E. |
| `base/known_issues.md` | numpy bool serialization, watertight check, library deps. |

## sdk/4/ — Trimesh 4.x

- `sdk/4/notes.md` — version-specific surface notes.

---

## Hard constraints

1. **`m.volume` only meaningful for watertight meshes.** Always check
   `m.is_watertight` first, repair if needed.
2. **Boolean ops require a backend** (manifold3d, scad, or blender).
   `m.intersection(...)` raises if none is installed; install
   `pip install manifold3d` for pure-pip.
3. **JSON-serialize numpy bools / floats explicitly**: cast via
   `bool(...)` / `float(...)` — `numpy.bool_` is NOT json-serializable.
4. **Acceptance != "ran without error"**. Validate volume/area against
   analytical (e.g. box V=L*W*H, sphere V=4/3πr³) for primitives, or
   against a known-good reference STL for complex geometry.
5. **Print results as JSON on the last stdout line.**

---

## Required protocol

1. Gather inputs:
   - **Category A:** input mesh path or generation params, expected
     property bounds, acceptance criterion.
   - **Category B:** repair tolerance, sampling density, output format.
2. `sim check trimesh`.
3. Write `.py` per `base/reference/workflow.md`.
4. `sim lint script.py`.
5. `sim run script.py --solver trimesh`.
6. Validate JSON.
