---
name: gmsh-sim
description: Use when driving Gmsh (finite-element mesh generator) via .geo DSL scripts or Python scripts using the gmsh API — 2D/3D meshing, CAD import, boundary layers, export to downstream solvers (CalculiX, OpenFOAM, FEniCS, SU2) through sim runtime one-shot execution.
---

# gmsh-sim

You are connected to **Gmsh** via sim-cli. This file is the **index** —
see the sections below for content.

Gmsh is an open-source finite-element mesh generator. It is a
**pre-processor** (not a solver). Its "result" is a mesh file (`.msh`)
that feeds downstream solvers like CalculiX, OpenFOAM, FEniCS, SU2.

Two input forms:

- **`.geo`** — Gmsh native DSL (SetFactory, Point, Sphere, Physical Volume, ...)
- **`.py`** — Python scripts that `import gmsh` and call the API

Both are run by sim via subprocess. `.geo` goes through Gmsh's CLI
wrapper; `.py` runs as plain Python (the script itself does
`gmsh.initialize() / .finalize()`).

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/geo_scripting.md` | GEO kernel DSL basics: Point/Line/Circle/Surface/Volume, Physical groups, OpenCASCADE. |
| `base/reference/python_api.md` | gmsh Python API patterns (initialize/add/occ/synchronize/mesh.generate/write). |
| `base/reference/mesh_formats.md` | .msh v2 vs v4 format, export targets for downstream solvers. |
| `base/snippets/01_sphere_mesh.geo` | Verified unit-sphere mesh snippet. |
| `base/known_issues.md` | Shebang on PATH, pip wheel vs system binary, msh2 vs msh4. |

## solver/4.15/ — Gmsh 4.15 specifics

- `solver/4.15/notes.md` — provenance, capabilities, format defaults.

---

## Hard constraints

1. **Gmsh is a mesher, not a solver.** Acceptance = mesh topology
   (node/element count, bbox, physical-group tags), NOT physical state.
2. **Always define Physical groups** when the mesh feeds a downstream
   solver — untagged entities are NOT exported by default.
3. **OpenCASCADE kernel requires `synchronize()`** before meshing or
   querying entities, after any boolean/create operation.
4. **Default output format is MSH 4.1**; many downstream solvers need
   MSH 2.2 (`-format msh22` flag).
5. **Never confuse `Mesh.<option> = ...` (config) with geometry
   commands** — a .geo containing only options has no geometry to mesh.

---

## Required protocol

After `sim check gmsh` confirms availability: gather Category A inputs
from user (geometry intent, target mesh size, physical group semantics,
downstream solver format). Write `.geo` or `.py`. Lint with `sim lint`.
Run with `sim run --solver gmsh`. Validate via JSON output from script
(node/element counts, bbox). Hand off `.msh` to downstream solver driver.
