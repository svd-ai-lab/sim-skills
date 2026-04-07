---
name: fluent-sim
description: Use when an agent or engineer needs to drive an Ansys Fluent meshing or solver session through the sim runtime — incremental snippet execution, single-file workflows, persistent sessions via `sim connect`/`sim exec`/`sim inspect`, or one-shot script runs.
---

# fluent-sim

Control protocol for running **Ansys Fluent** through the `sim` runtime. This is a *runtime control* skill, not a PyFluent API reference, not a script generator, and not a CFD tutorial.

## Scope boundary

| Ordinary scripting view | Runtime control view (this skill) |
|---|---|
| Write a Python script, run it end-to-end | Connect to a live session, execute steps, query state, decide next action |
| Success = script exits 0 | Success = acceptance criteria verified against actual session state |
| Errors surface at the end | Errors detected after each step; agent decides to continue, adjust, or stop |
| Missing inputs → runtime crash | Missing inputs detected *before* first snippet is sent |

This matters because Fluent workflows are **long, stateful, and expensive** — a wrong assumption at step 2 that crashes at step 12 wastes real compute and engineer time.

## When to use

Use this skill when **all three** are true:

1. The task involves Ansys Fluent (meshing, solving, or result extraction)
2. Execution happens through the sim CLI (`sim connect` / `sim exec` / `sim inspect` / `sim disconnect`)
3. The agent must decide what to do next based on current session state

**Do NOT use** for:
- Pure PyFluent API lookup → see `reference/pyfluent/`
- General Python or CFD questions unrelated to sim sessions

## Execution styles

**Style A — Incremental (default for complex workflows)**
Each step is a separate `sim exec` call. After each step the agent queries `last.result` and decides whether to continue, adjust, or stop. Best when mid-step feedback matters.

**Style B — Single-file**
All steps in one script submitted as a single `sim exec`. Valid when the workflow is well-understood and the user wants a single reviewable artifact. The script still uses the injected `solver` / `meshing` objects — it does NOT call `launch_fluent()`.

If a user asks "give me a complete script I can review and run myself", offer Style B. Don't redirect them away.

## Hard constraint — never call `launch_fluent()` in a snippet

`pyfluent.launch_fluent()` starts a new Fluent process. Inside a sim session the process is already running — calling it again starts a second conflicting instance. This applies to both styles.

If a user explicitly asks for a script starting from `launch_fluent()`, explain the constraint and offer the sim-managed equivalent (`sim connect` + snippet using the injected `solver`).

## Required protocol

### Step 0 — Parse task intent
Identify workflow type (meshing / solver / extraction). Load the corresponding template from [`reference/task_templates.md`](reference/task_templates.md).

**Every "Must ask if missing = YES" item from the loaded template is automatically a Category A input** — including meshing geometry parameters (length unit, max surface size, volume fill type, hex cell length…). Never infer these from a reference example filename.

### Step 0.5 — Detect PyFluent version
After connecting:
```
sim exec "import ansys.fluent.core as pf; _result = {'pyfluent_version': pf.__version__}"
```
Use the major.minor (e.g. `0.38`) to load reference docs from `reference/pyfluent/<version>/`. If no matching version dir exists, use the latest and rely on API discovery patterns ([`reference/pyfluent/api_discovery.md`](reference/pyfluent/api_discovery.md)) when calls fail. **Never hardcode version branches in snippets.**

### Step 1 — Check for missing inputs
Before sending any code to `sim exec`, verify:
- All "Must ask if missing = YES" items from the template
- All Category A inputs (see Input Validation below)
- **Acceptance criteria — these are required inputs, not optional metadata.** Verify the user has stated *what to extract* and *what counts as success*. Phrases like "跑完就好" / "just run it" do NOT constitute acceptance criteria; ask for an outcome.

### Step 2 — Connect
```
sim connect --mode <meshing|solver> --ui-mode <gui|no_gui> --processors <N>
```
Verify with `sim inspect session.summary` that `connected=true` and `mode` matches.

### Step 3 — Execute steps incrementally
Each workflow step = one `sim exec --code-file <tmp.py> --label <label>`. After each step check `sim inspect last.result` for `ok=true` before proceeding. See [`reference/runtime_patterns.md`](reference/runtime_patterns.md).

### Step 4 — Evaluate against acceptance criteria
After the final step, evaluate `sim inspect session.summary` and `sim inspect last.result` against [`reference/acceptance_checklists.md`](reference/acceptance_checklists.md).

**Context-completeness check** (required before declaring complete or incomplete): if responding to a mid-task state query and the original task context is unavailable, do **not** default any `[REQUIRED if X requested]` checklist item to "not applicable". Ask: "What were the original acceptance criteria?"

### Step 5 — Disconnect and report
```
sim disconnect
```
Report what was completed, what was verified, and any extracted values.

## Input validation policy

**Category A — Physical decision inputs (MUST ASK if absent).** Define what the simulation physically represents.

| Input category | Examples |
|---|---|
| File paths | Geometry (`.pmdb`), case (`.cas.h5`), data (`.dat.h5`) |
| Workflow type | Watertight / Fault-tolerant / Solver-only |
| Solver physics | Viscous model, turbulence, energy on/off |
| Boundary conditions | Inlet velocity / temperature, outlet type and parameters |
| Material | Fluid identity, density, viscosity |
| Initialization intent | Re-init from scratch, or continue from existing `.dat`? |
| Acceptance criteria | What quantity, what numerical range / threshold |

**Category B — Operational inputs (MAY DEFAULT; always disclose).**

| Parameter | Default | When acceptable |
|---|---|---|
| `--processors` | 2 | Low-cost validation |
| `--ui-mode` | `no_gui` | Automated / headless |
| Length unit | `m` | Unless filename suggests otherwise |
| Iteration count | 20 | Smoke tests only, not production |

**Category C — File-derivable (INFER; confirm if critical).** Boundary zone names, whether `.dat` exists, mesh scale — read from the actual provided files via a diagnostic snippet, not from reference examples.

### Reference example values are NOT defaults

Values in `reference/pyfluent/0.38/examples/` (e.g., `0.4 m/s` cold-inlet velocity in `mixing_elbow_settings_api.md`) describe a specific test case. They are **not** industry defaults and must **never** be silently applied to a different task. You may *offer* them: "the mixing_elbow example uses 0.4 m/s — would you like to use those values?" but wait for explicit confirmation. User pressure ("just use defaults") does not override this for Category A.

### Conflicting inputs

If two user-provided inputs cannot both be satisfied: name the conflict, explain why, offer alternatives, ask which to honor. Do **not** silently pick one and discard the other (e.g. "pressure outlet" + "fixed outlet velocity 0.5 m/s" — naming 0.5 m/s as backflow is an unannounced substitution).

## When to stop and escalate

- `sim exec` returns non-zero exit code
- `sim inspect last.result` returns `ok=false`
- A snippet raises an exception (visible in `last.result.stderr`)
- Session state inconsistent with expectations
- Acceptance checklist cannot be satisfied

**Do not silently retry failed steps.** Report with the relevant `last.result` fields.

## Critical: sim context vs. standalone API

Reference docs (`reference/pyfluent/...`) use the **standalone PyFluent API** (`pyfluent.launch_fluent()`, `pyfluent.Solver.from_install()`). In a sim snippet you do **NOT** call `launch_fluent()`. The session is live; `solver` / `meshing` are injected into the snippet namespace.

| Reference doc pattern | sim snippet equivalent |
|---|---|
| `solver = pyfluent.Solver.from_install()` | *(omit — already available)* |
| `meshing = pyfluent.Meshing.from_install()` | *(omit — already available)* |
| `solver.settings.setup.boundary_conditions…` | same path, use injected `solver` |
| `meshing.workflow.TaskObject[…]` | same path, use injected `meshing` |

## File index

### Top-level
- `SKILL.md` — this file
- `LICENSE` — Apache-2.0

## Install / quick start

```bash
# Install sim with the Fluent driver (from GitHub — not yet on PyPI)
pip install "git+https://github.com/svd-ai-lab/sim-cli.git#egg=sim-cli[fluent]"

# Run integration tests (needs a running Fluent session)
pytest tests/ -v
```

### `reference/` — domain knowledge
| File | When to read |
|---|---|
| `reference/runtime_patterns.md` | Patterns for the persistent-session control loop |
| `reference/task_templates.md` | Task-type templates (meshing / solver / extraction) — load the matching template at Step 0 |
| `reference/acceptance_checklists.md` | What "complete" means for each task type — used at Step 4 |
| `reference/pyfluent/README.md` | Index into curated PyFluent 0.38 reference docs |
| `reference/pyfluent/api_discovery.md` | How to discover the right `solver.settings.*` paths at runtime when an `AttributeError` happens |
| `reference/pyfluent/tui_vs_settings.md` | When to use legacy TUI commands vs the `settings` API |

### `workflows/` — end-to-end demos
| File | Demo |
|---|---|
| `workflows/demo_meshing_watertight.py` | Watertight geometry meshing |
| `workflows/demo_meshing_fault_tolerant.py` | Fault-tolerant meshing variant |
| `workflows/demo_watertight_via_driver.py` | Same workflow driven through `PyFluentDriver` |
| `workflows/demo_solver_exhaust.py` | Solver-side exhaust manifold case |
| `workflows/flipchip_thermal/demo_flipchip_thermal.py` | Flip-chip thermal demo (see flipchip_thermal/README.md) |

### `snippets/` — reusable `sim exec` snippets (numbered for canonical order)
```
00_diagnose_zones.py            01_read_case.py             02_mesh_check.py
03_setup_physics.py             04_setup_material.py        05_diag_bc_structure.py
05a_setup_bcs_ex01_ex05.py      05b_setup_bcs_ex02.py       06_hybrid_init.py
07_run_150_iter.py              08a_extract_outlet_temp.py  08b_extract_mass_weighted_temp.py
08c_extract_all_fields.py
```

### `tests/` — pytest integration tests
- `tests/conftest.py`, `tests/test_integration.py` — run against a live `sim serve` + Fluent license

### `skill_tests/` — protocol acceptance test cases (not pytest)
- `skill_tests/execution_test_cases_v0.md` — manual execution test cases (EX-01..EX-05)
- `skill_tests/execution_test_protocol.md` — acceptance protocol for the test cases
- `skill_tests/nl_test_cases.md`, `skill_tests/nl_behavior_test_protocol.md` — natural-language test cases for skill validation

## v0 limitations

- Post-processing & XY plot extraction: not covered
- Parametric / DoE loops: not covered
- Error recovery (e.g. re-mesh on failure): not covered
- Multi-zone / multi-region meshing: not covered
- Journal file replay: not covered

These are v1 candidates.
