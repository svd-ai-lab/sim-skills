---
name: icem-sim
description: "Use when running Ansys ICEM CFD meshing scripts — Tcl batch meshing via med_batch.exe, structured hex blocking, unstructured tetra generation, mesh export to Fluent/CFX/MAPDL/Abaqus formats"
---

# ICEM CFD Skill

## Identity

| Field | Value |
|---|---|
| Solver | Ansys ICEM CFD (meshing preprocessor) |
| Execution | Batch Tcl: `icemcfd.bat -batch -script <file.tcl>` |
| Session | **No** — ICEM meshing is batch-oriented, no persistent session. |
| SDK | None. Tcl 8.3.3 scripting via `ic_*` command API. |
| Script language | Tcl (`.tcl`, `.rpl` replay files) |
| Input geometry | `.tin` (native), `.stl`, `.igs` (IGES), CAD via converters |
| Output mesh | 143 export interfaces (Fluent `.msh`, CFX, ANSYS `.inp`, Abaqus, LS-DYNA, Nastran, CGNS, etc.) |

## Scope

- **In scope**: Running ICEM Tcl batch scripts, unstructured tetra
  meshing (`ic_uns_*`), hex blocking (`ic_hex_*`), geometry import
  (`ic_load_tetin`, `ic_geo_import_*`), boundary conditions
  (`ic_boco_*`), mesh export to solver formats.
- **Out of scope**: Interactive GUI operations (display, rotation,
  zooming), CAD creation (use SpaceClaim or CATIA), solver execution
  (use the corresponding solver driver: fluent, cfx, mapdl, etc.).

## Hard constraints

1. **Call `ic_batch_mode` (no arguments) at script top**. Without it,
   output interfaces may attempt interactive prompts that hang
   `med_batch.exe`. Note: `ic_batch_mode 1` throws "wrong # args"
   (see KI-008) — it's a toggle, not a setter.
2. **End scripts with `exit 0`**. `med_batch.exe` does not auto-exit
   after script completion — omitting `exit` causes a hang.
3. **Geometry must be watertight for tetra**. Open surfaces produce
   zero-element meshes with no error message.
4. **Forward slashes in paths**. Even on Windows, use `C:/sim/model.tin`
   not `C:\sim\model.tin` — Tcl backslash-escapes break paths.
5. **No display commands in batch**. `ic_display_*`, `ic_view_*`,
   `ic_screen_*` require a GUI and fail silently in batch mode.
6. **Tcl 8.4 limitations**. Documented as 8.3.3 but actual version is
   8.4.11 (on 24.1). No `lmap`, no `dict`. `{*}` expansion works.
7. **Wrap ic_* calls in `catch`**. ICEM Tcl commands print errors to
   stderr but return empty string — use
   `if {[catch {ic_uns_run_mesh} err]} { puts "ERROR: $err"; exit 1 }`
   to detect failures.

## File index

| Path | Purpose |
|---|---|
| `base/reference/icem_tcl_api.md` | `ic_*` command families, batch mode, gotchas |
| `base/reference/output_formats.md` | 143 export interfaces, major solver exports |
| `base/reference/mesh_workflow.md` | Tetra vs hex patterns, quality metrics, batch caveats |
| `base/snippets/` | Smoke tests (Phase 1) |
| `base/known_issues.md` | Discovered failure modes |
| `solver/24.1/notes.md` | ICEM 24.1 Windows install notes |

## Required protocol

### Before writing a script

1. Read `base/reference/icem_tcl_api.md` — understand the `ic_*` command
   families and batch-mode conventions.
2. Read `base/reference/mesh_workflow.md` — pick tetra or hex depending
   on the task.
3. Read `base/reference/output_formats.md` — pick the right export
   interface for the downstream solver.

### While writing

- Start with `ic_batch_mode 1` and end with `exit 0`.
- Use `catch` around critical `ic_*` calls.
- Forward slashes in all paths.
- Print structured JSON as the last line of stdout (sim parse_output
  convention):
  ```tcl
  puts "{\"ok\": true, \"nodes\": 1234, \"elements\": 5678}"
  exit 0
  ```

### Acceptance gates

| Gate | Check |
|---|---|
| 1 — Exit | `exit_code == 0` |
| 2 — Mesh generated | Output file exists and size > 0 |
| 3 — Element count | > 0 elements in output (zero = watertight failure) |
| 4 — Quality | Determinant > 0.3 (hex) or skewness < 0.9 (tetra) |

## Layered content

| Layer | When to consult | File |
|---|---|---|
| `base/` | Always | Above |
| `solver/24.1/` | ICEM 24.1 / 2024 R1 | `solver/24.1/notes.md` |
| `solver/24.2/` | ICEM 24.2 / 2024 R2 | `solver/24.2/notes.md` |
| `solver/25.1/` | ICEM 25.1 / 2025 R1 | `solver/25.1/notes.md` |
| `solver/25.2/` | ICEM 25.2 / 2025 R2 | `solver/25.2/notes.md` |
