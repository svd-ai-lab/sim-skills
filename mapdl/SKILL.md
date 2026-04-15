---
name: mapdl-sim
description: "Use when running Ansys MAPDL simulations — PyMAPDL Python scripts (launch_mapdl), static/modal/thermal/harmonic analyses, .rst result extraction, headless PyVista plots, or legacy .dat/.mac input files via mapdl.input()"
---

# MAPDL Skill

## Identity

| Field | Value |
|---|---|
| Solver | Ansys MAPDL (implicit structural / thermal / harmonic / modal) |
| Execution | gRPC server (`ANSYS<ver>.exe -grpc`, default port 50052) |
| Session | **Yes** (`supports_session = True`) — live `Mapdl` gRPC client held across `sim exec` calls; snippets run in sim's Python namespace. |
| SDK | `ansys-mapdl-core` (PyMAPDL) — Python client to the MAPDL gRPC server |
| Script language | Python (PyMAPDL); legacy APDL `.dat`/`.mac` via `mapdl.input(...)` |
| Post-processing | `mapdl.post_processing.*` / `mapdl.result.*` (PyVista, off-screen capable) |

## Scope

- **In scope**: Running PyMAPDL Python scripts via `sim run`, static
  structural / modal / transient thermal / harmonic response analyses,
  headless result extraction, headless PNG rendering of nodal fields,
  legacy APDL deck consumption via `mapdl.input(...)`.
- **Out of scope**: Geometry creation from CAD (use Workbench or
  SpaceClaim first, then `.igs` / `.sat` into MAPDL), mesh generation
  from third-party formats (use ANSA), explicit dynamics (use LS-DYNA).

## Hard constraints

1. **Pair every processor-switch with `finish()`**. Every `prep7()` /
   `solution()` / `post1()` must be followed by a later `finish()`
   before the next switch. Forgetting `finish()` silently routes
   commands to the wrong processor.
2. **Call `mapdl.allsel()` before `mapdl.solve()`**. A dangling
   selection from BC picking causes the solve to see only a subset
   of the model with no error.
3. **Call `set(1, 1)` in POST1 before querying results**. Skipping it
   returns zero-filled arrays without raising.
4. **Never read state inside `with mapdl.non_interactive:`**. Commands
   in that block are buffered, so `mapdl.parameters[...]` or
   `mapdl.mesh.nnum` will show stale values.
5. **Wrap lifetime in try/finally**. Exceptions before `mapdl.exit()`
   leave zombie `ANSYS<ver>.exe` processes — use `with launch_mapdl()
   as mapdl:` or an explicit `finally`.
6. **Use `np.nanmax` / `np.nanmean`**. Mid-side nodes of quadratic
   elements have NaN stress; aggregates must skip them.
7. **Unit system is not enforced**. Call `mapdl.units("SI")` (or your
   chosen system) once at the top — mixing systems silently gives
   wrong answers.

## File index

| Path | Purpose |
|---|---|
| `base/reference/pymapdl_api.md` | `launch_mapdl()` signature, env-var detection chain, lifecycle |
| `base/reference/mapdl_commands.md` | Pythonic vs raw APDL, `non_interactive`, legacy-deck conversion |
| `base/reference/postprocessing.md` | `post_processing.*`, `mapdl.result`, headless PNG rendering |
| `base/reference/analysis_workflow.md` | Skeletons for static / modal / thermal / harmonic analyses |
| `base/snippets/NN_<name>.py` | Self-contained Phase 1 smoke tests, run via `sim run` |
| `base/workflows/<name>/` | Tier A vendor verification examples with evidence |
| `base/known_issues.md` | Failure modes and their root cause |
| `sdk/0.72/notes.md` | PyMAPDL 0.72 API specifics |
| `solver/24.1/notes.md` | MAPDL 24.1 Windows install quirks |

## Required protocol

### Before building a new script

1. Read `base/reference/pymapdl_api.md` — understand `launch_mapdl()`
   detection chain, the `Mapdl` object lifecycle, and the `with`-block
   pattern.
2. Read `base/reference/analysis_workflow.md` — pick the skeleton
   matching your analysis type (static, modal, thermal, harmonic).
3. Read `base/reference/mapdl_commands.md` — decide Pythonic wrapper
   vs raw APDL for each command.

### While writing

- Start with a built-in VM file (`ansys.mapdl.core.examples.vmfiles["vm10"]`)
  rather than a synthetic geometry — it's vendor-validated.
- Use `mapdl.units("SI")` at the top.
- Every `prep7()` / `solution()` / `post1()` matched with later `finish()`.
- Before `solve()`: `mapdl.allsel()`.
- Before querying in POST1: `mapdl.set(1, 1)`.
- Print structured JSON as the last line of stdout — sim's
  `parse_output` convention. Example:
  ```python
  print(json.dumps({
      "ok": True,
      "max_disp_m": float(umag.max()),
      "max_seqv_pa": float(np.nanmax(seqv)),
  }))
  ```

### Physics-based acceptance gates

Every snippet must pass:

| Gate | Check |
|---|---|
| 1 — Exit | `exit_code == 0` AND script prints final JSON with `ok: true` |
| 2 — Structural: displacement | `0 < max_disp_m < 1.0` (if > 1 m, model is unconstrained) |
| 3 — Structural: stress | `0 < max_seqv_pa < 1e12` (> 1 TPa is unphysical) |
| 4 — Modal: frequencies | all `freq > 0`, first mode > 0.01 Hz |
| 5 — Thermal: temperature | within physical range for the problem |

### Headless visualization (Step 8.5)

Every workflow must emit **at least one PNG** via
`mapdl.post_processing.plot_*(savefig=..., off_screen=True)` or
`mapdl.result.plot_*(savefig=..., off_screen=True)` — not via
GUI automation. See `reference/postprocessing.md`.

## Layered content

| Layer | When to consult | File |
|---|---|---|
| `base/` | Always | Above |
| `sdk/0.72/` | PyMAPDL 0.68 ≤ SDK < 0.80 | `sdk/0.72/notes.md` |
| `solver/24.1/` | MAPDL 24.1 / 2024 R1 | `solver/24.1/notes.md` |
| `solver/24.2/` | MAPDL 24.2 / 2024 R2 | `solver/24.2/notes.md` |
| `solver/25.1/` | MAPDL 25.1 / 2025 R1 | `solver/25.1/notes.md` |
| `solver/25.2/` | MAPDL 25.2 / 2025 R2 | `solver/25.2/notes.md` |

## Execution modes

Both one-shot and persistent session are supported:

| Mode | Command | When to use |
|---|---|---|
| **One-shot** | `sim run script.py --solver mapdl` | Script is self-contained, runs → exits in one shot. Driver launches MAPDL, runs the user's `launch_mapdl()` script, tears down. Phase 1 — verified against 2D beam + 3D notch (see `workflows/mapdl_beam/`, `workflows/notch_3d/`). |
| **Session** | `sim connect --solver mapdl` → `sim exec ...` → `sim inspect ...` → `sim disconnect` | Agents incrementally build / probe / solve / post-process against a live `Mapdl` gRPC client. Phase 2 — verified via `workflows/mapdl_beam_session/`. |

Session namespace exposed to `sim exec` snippets: `mapdl`, `np`,
`launch_mapdl`, `workdir`, `_result`. Inspect targets:
`session.summary`, `mesh.summary`, `workdir.files`, `results.summary`,
`last.result`.

## Build order (historical)

Phase 1 was shipped first (`sim run` against vendor verification
examples) per the driver-development guide "one-shot first" rule;
Phase 2 (session) was added once Phase 1 was verified. The same 2D
I-beam test case runs identically through both modes — same
max-deflection (-0.0265 cm) and same visible UZ contour PNG.
