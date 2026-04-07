---
name: flotherm-sim
description: Use when running Simcenter Flotherm 2504 thermal cases through the sim runtime — Phase A `.pack` execution via Win32 API automation playing back FloSCRIPT XML in the Flotherm GUI. Headless batch mode is currently broken (vendor defect).
---

# flotherm-sim

Control protocol for running **Siemens Simcenter Flotherm 2504** thermal simulations through the `sim` runtime.

## Identity

- **Solver**: Simcenter Flotherm 2504 (3D CFD thermal simulation for electronics)
- **Driver**: `sim.drivers.flotherm.FlothermDriver`
- **Execution**: GUI + Win32 API automation (Macro > Play FloSCRIPT)
- **Script format**: FloSCRIPT XML (Drawing Board syntax)

## Phases

| Phase | Status | Description |
|---|---|---|
| **A** | Current | Batch `.pack` execution via FloSCRIPT playback |
| **B** | Planned | FloSCRIPT XML authoring + batch |
| **C** | Planned | Live `flogate_cl` session |

## Proven execution path

```
driver.launch()       →  explorer.exe flotherm.exe (GUI starts)
driver.load_project() →  unpack .pack to FLOUSERDIR
driver.submit_job()   →  generate FloSCRIPT XML
                         →  Win32 API: Macro > Play FloSCRIPT > file dialog
driver.watch_job()    →  poll field files + logit for completion
driver.disconnect()   →  close session
```

**Verified**: Mobile_Demo-Steady_State, 153,449 grid cells, steady-state converged.

## When to use

- Task is a Flotherm thermal simulation (`.pack` file or FloSCRIPT `.xml`)
- Execution happens through the sim Flotherm driver
- A Flotherm GUI desktop session is available (Phase A is GUI-only — see Known Issues)

**Out of scope:** headless batch mode (vendor defect, see Known Issues), FloSCRIPT authoring from scratch, persistent multi-step sessions, post-processing visualization.

## Hard constraints — correct FloSCRIPT syntax

**Use Drawing Board commands.** Do NOT use `<external_command process="CommandCentre">`.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xml_log_file version="1.0">
    <project_unlock project_name="{PROJECT_NAME}"/>
    <project_load   project_name="{PROJECT_NAME}"/>
    <start          start_type="solver"/>
</xml_log_file>
```

Rules:
- `project_unlock` BEFORE `project_load` (releases stale locks)
- `<start start_type="solver"/>` triggers solve (NOT `<solve_all/>`)
- `<solve_all/>` is a CommandCentre command — **invalid in Drawing Board playback**
- Script must be saved as `.xml` and played via `Macro > Play FloSCRIPT`

## Required protocol

### Step 1 — Validate
```python
driver.connect()           # status="ok", version="2504"
driver.lint(pack_path)     # ok=True for valid .pack
driver.detect(pack_path)   # True for .pack and FloSCRIPT .xml
```

### Step 2 — Launch session
```python
driver.launch(ui_mode="gui")  # starts Flotherm GUI, returns session dict
```

### Step 3 — Load project and submit solve
```python
driver.load_project(Path("model.pack"))  # unpack to FLOUSERDIR
job = driver.submit_job(label="solve")    # generate + dispatch FloSCRIPT
```

### Step 4 — Monitor completion
```python
job = driver.watch_job(job["job_id"], timeout=300)
# job["state"]: "succeeded" | "failed" | "timeout" | "waiting_backend"
```

### Step 5 — Check results
```python
artifacts = driver.query_artifacts()
# artifacts["modified_fields"]: list of changed field files
# Check logit for "status 3 normal exit" = convergence
```

### Step 6 — Report and disconnect
```python
driver.disconnect()
```

## Acceptance criteria

**`exit_code == 0` alone is NOT sufficient.** Must verify:

| Check | How |
|---|---|
| Field files modified | `msp_*/end/Temperature` mtime changed |
| No fatal errors | `floerror.log` has no `E/11029` or `E/9012` |
| Solver converged | `logit` contains `status 3 normal exit` |
| Grid cells > 1 | `logit` header shows real grid (not 1x1 fallback) |

See [`reference/acceptance_checklists.md`](reference/acceptance_checklists.md).

## Input validation policy

Before calling `run_file()` or `submit_job()`, always validate:
- `.pack` file exists and `driver.lint()` returns `ok=True`
- `driver.connect()` returns `status="ok"` (Flotherm installed)
- Acceptance criterion is defined (not just "run it")

## When to stop and escalate

- `driver.lint()` returns `ok=False`
- `driver.connect()` returns `status != "ok"`
- `job["state"] == "failed"` (check `job["errors"]` for details)
- `job["state"] == "timeout"`
- `floerror.log` contains `E/11029` or `E/9012` (fatal solver errors)

## Environment requirements

- `SALT_LICENSE_SERVER` must be set (driver reads from Windows registry automatically)
- Flotherm GUI must be launched via `flotherm.exe` (NOT `flotherm.bat`)
- `flotherm.bat -b` and `-f` flags are non-functional in 2504 — see known_issues.md

## Known issues (highlights)

See [`known_issues.md`](known_issues.md) for the full list:

1. **`flotherm.bat -b` broken** — `registerStart runTable exception` (vendor defect)
2. **`flotherm.bat -f` broken** — Project Manager crash or ignores `-f` argument
3. **`external_command` syntax invalid** — Use Drawing Board commands only
4. **Project lock files** — Must `project_unlock` before `project_load`
5. **`SALT_LICENSE_SERVER`** — Must point to a `license.dat` file, not `29000@hostname`

## File index

### Top-level
- `SKILL.md` — this file
- `known_issues.md` — Phase A bugs and workarounds
- `pytest.ini` — pytest config

### `reference/` — control loop, templates, checklists
- `reference/runtime_patterns.md` — Phase A control loop patterns
- `reference/task_templates.md` — task-level protocols mapped to user intents
- `reference/acceptance_checklists.md` — what "complete" means for a Flotherm batch run

### `docs/` — investigation reports
- `docs/flotherm_env_shell_probe_report.md` — env shell investigation (paths, env vars, license discovery)
- `docs/flotherm_runtime_validation_report.md` — end-to-end Phase A validation against real `.pack` files

### `workflows/` — end-to-end demos
End-to-end demos. (Currently scaffolded — see spec / future Phase B work for FloSCRIPT examples.)

### `tests/` — pytest unit + integration
- `tests/test_skill_structure.py` — structure tests; do not need Flotherm installed
- `tests/test_batch_execution.py` — Phase A batch execution tests; require Flotherm 2504; marker `slow` for real solves
- `tests/test_runtime.py` — runtime layer tests
- `tests/conftest.py` — fixtures and skip logic

### `skill_tests/` — protocol acceptance test cases (not pytest)
- `skill_tests/execution_test_cases_v1.md` — Phase A test cases EX-01..EX-07
- `skill_tests/execution_test_protocol.md` — acceptance protocol

## Quick start

```bash
# Structure tests (no Flotherm needed)
pytest tests/test_skill_structure.py -v

# Execution tests (Flotherm 2504 required)
pytest tests/test_batch_execution.py -v -m "not slow"   # fast checks only
pytest tests/test_batch_execution.py -v                  # includes real solve
```

## Requirements

- Simcenter Flotherm 2504 installed and licensed
- `sim-cli` with the Flotherm driver (`FlothermDriver` in `sim.drivers.flotherm`)
- Interactive Windows desktop session (Phase A is GUI-only)
