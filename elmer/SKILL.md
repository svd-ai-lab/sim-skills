---
name: elmer-sim
description: Use when driving Elmer FEM (open-source multi-physics finite-element suite from CSC-IT) via `.sif` solver-input files — heat/elasticity/electromagnetics/fluid multiphysics, through sim runtime one-shot execution on Linux.
---

# elmer-sim

You are connected to **Elmer FEM** via sim-cli.

Elmer is an open-source multi-physics FEM code from CSC (Finland). A
case is defined by:

- **`.sif`** — Solver Input File (block-structured text)
- **mesh directory** — referenced via `Mesh DB "." "meshname"` in
  Header block; contains `mesh.header`, `mesh.nodes`, `mesh.elements`,
  `mesh.boundary`

Execution: `ElmerSolver case.sif`. Output: `case.vtu` (ParaView, name
set by `Post File` in Simulation block).

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/sif_blocks.md` | `.sif` block structure (Header, Simulation, Body, Material, Solver, BC). |
| `base/reference/mesh_workflow.md` | ElmerGrid usage; native mesh format; Gmsh → Elmer conversion. |
| `base/reference/solver_catalog.md` | Built-in solvers: HeatSolve, StressSolver, MagnetoDynamics, etc. |
| `base/snippets/01_heat_square.sif` | Verified heat-equation E2E snippet. |
| `base/known_issues.md` | Build flags, mesh conversion quirks. |

## solver/26.1/ — Elmer FEM 26.1 specifics

- `solver/26.1/notes.md` — source build info, dependencies.

---

## Hard constraints

1. **Mesh directory must exist before solving**. Reference via
   `Mesh DB "dir" "meshname"` means files live in `<dir>/<meshname>/`.
2. **Block ordering matters**: Header → Simulation → Constants → Body →
   Material → Body Force → Initial → Equation → Solver → BC.
3. **Active Solvers list** in an Equation block ties solvers to bodies.
   Bodies without an Equation reference are passive.
4. **Acceptance != exit code.** Check the `.vtu` output or stdout
   residual history for physical validity.
5. **`End` closes every block** — missing `End` causes cryptic parse
   errors far from the mistake.

---

## Required protocol

After `sim check elmer`: gather Category A inputs (physics, geometry
source for mesh, BCs, material properties, acceptance criteria).
Generate mesh (ElmerGrid from .grd, or Gmsh→Elmer). Write `.sif`.
Lint with `sim lint`. Run with `sim run --solver elmer`. Parse `.vtu`
or stdout for validation.
