---
name: meshio-sim
description: Use when bridging mesh formats across solvers — converting Gmsh .msh to CalculiX .inp, Abaqus to VTK, OpenFOAM to XDMF, etc. via the pure-Python meshio library. Covers 20+ mesh formats.
---

# meshio-sim

You are connected to **meshio** via sim-cli.

meshio is a Python library/CLI for converting between mesh formats. It's
the **glue** in sim's multi-solver ecosystem:

- **Gmsh → CalculiX / Elmer / SU2** (pre-processor → solver)
- **OpenFOAM → VTK** (post-processing)
- **CGNS ↔ XDMF ↔ MSH** (cross-tool data exchange)

No separate binary. Two usage modes:
1. Python scripts `import meshio` (driven by sim)
2. CLI: `meshio convert in.msh out.vtk`, `meshio info mesh.vtu`

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/formats.md` | 20+ mesh formats matrix + pick one. |
| `base/reference/api.md` | `meshio.read/write/Mesh/convert` + cells structure. |
| `base/reference/cli.md` | `meshio convert/info/compress` usage. |
| `base/snippets/01_gmsh_to_vtk.py` | Verified conversion snippet. |
| `base/known_issues.md` | Cell-type naming, physical-tag preservation, .xdmf h5py dep. |

## sdk/5/ — meshio 5.x

- `sdk/5/notes.md` — API stability across 5.x.

---

## Hard constraints

1. **meshio is a bridge, not a solver.** Success = mesh topology
   preserved across formats (point count, cell count, bbox).
2. **Cell type names vary by format** — `"triangle"` in meshio maps to
   `CPS3` in Abaqus/CalculiX, type `2` in Gmsh v2 MSH, etc. Check the
   mapping table in `base/reference/formats.md`.
3. **Physical group preservation is format-dependent.** MSH→VTK loses
   physical tags; MSH→XDMF preserves them via cell data. Document in the
   conversion script.
4. **Never modify mesh in-place** — always read → transform → write to
   a new file for reproducibility.

---

## Required protocol

Gather: input format, output format, whether physical tags matter,
target solver (so we choose the right output format). Write `.py` that
reads the mesh, optionally filters cells / renames tags, writes the
new format. Validate via point/cell counts and bbox.
