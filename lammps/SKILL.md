---
name: lammps-sim
description: Use when driving LAMMPS (Large-scale Atomic/Molecular Massively Parallel Simulator) via `.in` / `.lmp` scripts — classical molecular dynamics, LJ/EAM/Tersoff/ReaxFF potentials, NVE/NVT/NPT ensembles, through sim runtime one-shot execution on Linux.
---

# lammps-sim

You are connected to **LAMMPS** via sim-cli.

LAMMPS is an open-source classical MD code from Sandia/Temple. Input is
a plain-text command script (`.in` or `.lmp` extension). Execution:

    lmp -in script.in

Output files in cwd:
  - `log.lammps` — thermo log + run info
  - `dump.*` — trajectory (if `dump` command present)
  - `restart.*` — restart (if `write_restart`)

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/script_structure.md` | Strict command ordering: init → system → potentials → run. |
| `base/reference/units_and_potentials.md` | Unit systems (lj, real, metal, si) and pair_style/pair_coeff. |
| `base/reference/ensembles.md` | NVE/NVT/NPT fixes, thermostats, barostats. |
| `base/reference/output.md` | thermo / dump / restart parsing. |
| `base/snippets/01_lj_nvt.in` | Verified LJ liquid NVT equilibration. |
| `base/known_issues.md` | Missing potential files, unit mismatch, neighbor errors. |

## solver/29Aug2024/ — stable release specifics

- `solver/29Aug2024/notes.md` — build provenance + serial limits.

---

## Hard constraints

1. **`units` must be the FIRST command** (besides comments) — everything
   downstream depends on it; changing mid-script invalidates the run.
2. **Command ordering is strict**: init → system definition → force
   fields + neighbors → fixes + output → run. Out-of-order = cryptic
   errors ("Illegal command" or "Lost atoms").
3. **Acceptance != exit code.** LAMMPS can exit 0 and produce
   unphysical results ("Lost atoms", NaN energies). Check `log.lammps`
   thermo for finite values.
4. **Potentials are unit-dependent** — an LJ `sigma=1.0` in `units lj`
   is NOT the same as in `units real`.
5. **One time-integration fix per atom group** — unless explicitly
   coordinated, overlapping `fix nvt` + `fix npt` corrupts the run.

---

## Required protocol

After `sim check lammps`: gather Category A inputs (unit system,
potentials, geometry source, ensemble, acceptance criteria). Write
`.in` script. Lint with `sim lint`. Run with `sim run --solver lammps`.
Parse `log.lammps` thermo for final state + validate against physics.
