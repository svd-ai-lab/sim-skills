---
name: su2-sim
description: Use when driving SU2 (open-source multi-physics CFD solver) via `.cfg` config files + `.su2` meshes — Euler/RANS/LES, adjoint design, multi-zone, through sim runtime one-shot execution on Linux.
---

# su2-sim

You are connected to **SU2** via sim-cli.

SU2 is an open-source multi-physics PDE solver suite (primary focus CFD)
developed at Stanford. The main binary is `SU2_CFD`. A case is:

- **`.cfg`** — plain-text config file (`KEYWORD= value`, `%` for comments)
- **`.su2`** — mesh file (SU2 native format, referenced via `MESH_FILENAME=`)

Execution: `SU2_CFD config.cfg`. Outputs land in cwd:

- `history.csv` — per-iteration convergence history
- `restart_flow.dat` — binary restart file
- `flow.vtu` + `surface_flow.vtu` — VTK for ParaView

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/config_syntax.md` | `.cfg` grammar + keyword families (solver, flow, markers, numerics, output). |
| `base/reference/markers_and_bcs.md` | How mesh markers map to boundary conditions. |
| `base/reference/solver_families.md` | Euler / RANS / LES / Adjoint / Multi-zone. |
| `base/reference/output_and_history.md` | history.csv columns, restart policy, VTU export. |
| `base/snippets/01_inviscid_bump.cfg` | Verified Euler bump case (100-iter convergence test). |
| `base/known_issues.md` | Output filename defaults, MPI builds, convergence tuning. |

## solver/8.4/ — SU2 8.4 specifics

- `solver/8.4/notes.md` — prebuilt binary details.

---

## Hard constraints

1. **Config keywords are fixed** — do not invent options. Check official
   wiki or `SU2_CFD --help` before adding a keyword.
2. **Marker names in `.cfg` must match mesh tags** — mismatched names
   silently skip boundary application.
3. **Acceptance != exit code.** `SU2_CFD` can exit 0 and still produce
   diverged garbage. Always check `history.csv` for residual drop.
4. **Compressible vs incompressible variable conventions differ** —
   `MACH_NUMBER` / `FREESTREAM_PRESSURE` are compressible; incompressible
   uses `INC_VELOCITY_INIT` / `INC_DENSITY_INIT`.
5. **Output files overwrite in place** — use a fresh working directory
   per run.

---

## Required protocol

After `sim check su2`: gather Category A inputs (physics type, freestream
conditions, geometry+mesh, boundary conditions, acceptance criteria).
Write `.cfg`. Lint with `sim lint`. Run with `sim run --solver su2`.
Validate via `history.csv` residual drop (typical: RMS[Rho] drops >=2
orders of magnitude for converged Euler/RANS).
