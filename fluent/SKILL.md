---
name: fluent-sim
description: Use when an agent or engineer needs to drive an Ansys Fluent meshing or solver session through the sim runtime — incremental snippet execution, single-file workflows, persistent sessions via `sim connect`/`sim exec`/`sim inspect`, or one-shot script runs.
---

# fluent-sim

You are connected to **Ansys Fluent** via sim-cli. This file is the
**index**. It tells you where to look for actual content — it does not
contain the content itself.

The `/connect` response told you which active layers apply via:

```json
"skills": {
  "root":               "<sim-skills>/fluent",
  "active_sdk_layer":   "0.38",   // or "0.37"
  "active_solver_layer":"25.2"    // or null
}
```

Always read the index for `base/`, then your active `sdk/<version>/`,
then your active `solver/<version>/`. Later layers override earlier
ones on identically-named files.

---

## base/ — always relevant

Concepts, terminology, and version-agnostic control patterns:

| Path | What's there |
|---|---|
| `base/reference/task_templates.md` | Per-workflow input templates with "Must ask if missing" lists. **Always read first** to identify Category A inputs before any `sim exec`. |
| `base/reference/runtime_patterns.md` | The incremental "execute → inspect last.result → decide → next" loop. The canonical control protocol. |
| `base/reference/acceptance_checklists.md` | Per-workflow acceptance criteria. Used to evaluate the final session state. |
| `base/reference/api_discovery.md` | `dir()` / `child_names` patterns for finding renamed attributes when an API call fails. |
| `base/reference/tui_vs_settings.md` | When to prefer the Settings API vs the legacy TUI. |
| `base/reference/pyfluent_overview.md` | Quick orientation: what PyFluent is, what each module does. |
| `base/snippets/` | Numbered EX-01 step snippets (`01_read_case.py` through `08c_extract_all_fields.py`). Built for the modern (0.38) dialect; portable to 0.37 with the material-accessor swap noted in `sdk/0.37/notes.md`. |
| `base/workflows/` | Multi-step demo scripts: meshing (watertight + fault-tolerant), solver exhaust manifold, flipchip thermal. |

## sdk/<active_sdk_layer>/ — PyFluent API specifics

Read the layer matching your `active_sdk_layer` field:

- `sdk/0.38/` — current PyFluent line.
  - `cheat_sheet.md` — most common API calls in one file.
  - `examples/` — full pyfluent.docs.pyansys.com examples (mixing_elbow,
    ahmed_body, conjugate_heat_transfer, …). Each is a working Python
    script you can quote from.
  - `user_guide/` — the upstream PyFluent user guide, mirrored. Search
    here when an API call surprises you.
- `sdk/0.37/` — legacy line.
  - `notes.md` — the one accessor difference vs 0.38 that bites EX-01.

## solver/<active_solver_layer>/ — Fluent release specifics

- `solver/25.2/` — Fluent 25R2 (v252) quirks (currently empty stub).

## skill_tests/ and tests/ (top-level, not part of the layered tree)

These are QA artifacts for the skill itself, not content the LLM should
load during a normal session:

- `skill_tests/` — natural-language and execution test cases used to
  validate the skill end-to-end against real Fluent.
- `tests/` — pytest integration tests.

---

## Hard constraints (apply to every session)

1. **Never call `pyfluent.launch_fluent()` from a snippet.** sim-cli
   already started the Fluent process. A second `launch_fluent()`
   spawns a conflicting instance.
2. **Never invent Category A defaults.** Geometry params, materials,
   BCs, acceptance criteria — if missing, ask the user.
3. **Acceptance ≠ exit code.** A snippet can return `ok=true` and the
   simulation can still be physically wrong. Validate against
   `base/reference/acceptance_checklists.md` after the final step.

---

## Required protocol (one paragraph)

After `/connect` succeeds: read the active task template from
`base/reference/task_templates.md`, gather Category A inputs from the
user, then execute incrementally per `base/reference/runtime_patterns.md`,
checking `last.result` after every step. Use snippets from
`base/snippets/` (translating material-accessor calls per
`sdk/<your-version>/notes.md` if applicable). After the final step,
evaluate against the relevant checklist in
`base/reference/acceptance_checklists.md`.

For the canonical end-to-end example (the EX-01 mixing-elbow case),
the snippet sequence is `01_read_case` → `02_mesh_check` →
`03_setup_physics` → `04_setup_material` → `05a_setup_bcs_ex01_ex05` →
`06_hybrid_init` → `07_run_150_iter` → `08a_extract_outlet_temp`,
followed by acceptance evaluation against the EX-01 row of
`acceptance_checklists.md`.
