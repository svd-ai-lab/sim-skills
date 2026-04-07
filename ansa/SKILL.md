---
name: ansa-sim
description: Use when running BETA CAE ANSA v25 pre-processor scripts through sim in headless batch mode (`ansa_win64.exe -execscript -nogui`). Phase 1 covers batch `.py` execution only — no persistent session, no GUI, no `.ansa` database manipulation without a script wrapper.
---

# ansa-sim

Control protocol for running **BETA CAE ANSA v25.0.0** (pre-processor) through the `sim` runtime.

## Identity

- **Solver**: BETA CAE ANSA v25.0.0 (pre-processor; ANSA does not solve, it builds/cleans/meshes models for downstream solvers — Nastran, Abaqus, LS-DYNA, OpenFOAM, …)
- **Driver**: `sim.drivers.ansa.AnsaDriver`
- **Execution model**: One-shot batch (`ansa_win64.exe -execscript -nogui`)
- **Phase**: 1 — batch `.py` script execution only
- **Verified**: 2026-04-03, 31 pytest + 4 real execution tests pass

## Scope boundary

Phase 1 covers batch execution of `.py` scripts that `import ansa`. The agent **can**:
- Validate scripts (syntax, imports, batch compatibility)
- Run scripts in headless mode
- Parse JSON output from scripts
- Report results

The agent **cannot**:
- Maintain a persistent ANSA session across multiple calls
- Interact with the ANSA GUI
- Open/modify `.ansa` databases without a script wrapper
- Run solvers (ANSA is a pre-processor)

## Execution model

```
lint(.py) → connect() → run_file(.py) → parse_output(stdout) → verify acceptance
```

## Required protocol

### Step 0 — Identify task type
Confirm the user has a `.py` ANSA script → load workflow template.

### Step 1 — Validate inputs
- `.py` file exists: `Path(script).exists()`
- Script is valid: `driver.lint(script).ok is True`
- ANSA installed: `driver.connect().status == "ok"`

→ Do not call `run_file()` until all three pass.

### Step 2 — Run
```python
result = driver.run_file(script)
```
May take 10 seconds to 10+ minutes. **Do not interrupt.**

### Step 3 — Evaluate result
1. `result.exit_code == 0`? → If non-zero: report and stop
2. `result.stderr` empty or warnings only? → If errors: report
3. `result.stdout` non-empty? → If empty: suspicious
4. Acceptance criterion? → `parse_output(result.stdout)`, compare values

→ **`exit_code=0` ALONE does NOT satisfy acceptance criterion.**

### Step 4 — Report
exit_code, duration_s, extracted values, stderr if non-empty.

## Input validation policy

**Category A — Must confirm before running:**
- `.py` script path
- Acceptance criterion (what "success" means)

**Category B — Derivable:**
- ANSA version: `driver.connect().version`
- Has `main()`: detected by linter

## When to stop and escalate

- `driver.lint()` returns `ok=False`
- `driver.connect()` returns `status != "ok"`
- `result.exit_code != 0`
- `result.stderr` contains ERROR or traceback
- Acceptance criterion not met

## Script convention

ANSA scripts should follow this pattern for sim integration:

```python
import json
import ansa
from ansa import base, session, constants

def main():
    """Entry point — called by ansa64.bat -execscript 'script.py|main()'."""
    session.New('discard')
    base.Open('/path/to/model.ansa')

    # ... perform operations ...

    result = {"element_count": 12345, "min_quality": 0.32, "ok": True}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
```

Key conventions:
- Define `main()` as entry point
- Print a single JSON line to stdout as the last output
- Use `session.New('discard')` to start clean
- Avoid GUI-only functions (`PickEntities`, `guitk`)

## ANSA Python API quick reference

### Core imports
```python
from ansa import base, constants, mesh, session
```

### Common operations
```python
# Set solver deck
base.SetCurrentDeck(constants.NASTRAN)  # ABAQUS, LSDYNA, FLUENT, etc.

# Collect entities
shells = base.CollectEntities(deck, None, "SHELL")
props  = base.CollectEntities(deck, None, "__PROPERTIES__")

# Read/write entity values
vals = entity.get_entity_values(deck, {"T", "PID", "Name"})
entity.set_entity_values(deck, {"Name": "new_name", "T": 2.5})

# Create entities
prop = base.CreateEntity(deck, "PSHELL", {"Name": "plate", "T": 1.0})
mat  = base.CreateEntity(deck, "MAT1", {"E": 210000.0, "NU": 0.3})

# File I/O
session.New('discard')
base.Open('/path/to/model.ansa')
base.SaveAs('/path/out.ansa')

# Element quality
skew = base.ElementQuality(elem, "SKEW")
off  = base.CalculateOffElements(comp)  # {'TOTAL OFF': n}

# Mesh repair
mesh.FixQuality()
mesh.ReconstructViolatingShells(expand_level)
```

### Common pitfalls
| Pitfall | Fix |
|---|---|
| `CollectEntities` arg 2 error | Use `None` for global scope, not a single entity |
| GUI functions in `-nogui` mode | Avoid `guitk.*`, `PickEntities` — linter warns |
| Deck mismatch | Entity ops must match the loaded deck |
| `ANSA_SRV` unresolved | Driver sets `ANSA_SRV=localhost` automatically |

## Automation capability assessment

Based on research (GitHub repos, conference papers, community forums):

- **No persistent session API** — ANSA has no external RPC/socket/COM interface
- **No attach-to-running-instance** — unlike MATLAB Engine or COMSOL LiveLink
- **`ansa` module is process-internal only** — cannot be imported from external Python
- **KOMVOS framework** dispatches batch jobs, not live sessions
- **One-shot batch is the only reliable automation path**

If persistent sessions become needed, the only viable (unofficial) approach is a self-hosted socket server script running inside ANSA's embedded Python.

## Environment requirements

- `ANSA_SRV=localhost` (set by driver automatically)
- ANSA v25.0.0 installed at standard path

## File index

### Top-level
- `SKILL.md` — this file
- `known_issues.md` — license, batch mode, gotchas
- `pytest.ini` — pytest config

### `reference/` — ANSA scripting docs
- `reference/ansa_api_reference.md` — distilled ANSA Python API reference
- `reference/ANSA_Scripting_User_Guide.md` — distilled scripting user guide
- `reference/youtube_ansa_api_research.md` — notes from ANSA-related video tutorials
- `reference/official_docs/` — subset of the official ANSA docs (intro, 10-min tutorial, interpreter, script editor, user guide, full API, batch-mesh API, CAD API, mesh API)

### `spec/` — design specs
- `spec/2026-04-02-ansa-sim-design.md` — Phase 1 design spec for the ansa-sim driver and skill

### `docs/` — investigation reports
- `docs/ansa_investigation_summary.md` — initial findings
- `docs/ansa_runtime_dev_report.md` — runtime / driver development report
- `docs/iap_remotecontrol_test_report.md` — test report for IAP RemoteControl mode
- `docs/ansa_final_report.md` — final Phase 1 report

### `tests/` — pytest unit + integration
- `tests/test_ansa_driver.py` — driver unit tests
- `tests/test_runtime.py` — runtime layer tests
- `tests/test_pipeline.py`, `tests/test_geometry_pipeline.py` — pipeline tests
- `tests/conftest.py` — fixtures, skip-logic for missing ANSA
- `tests/fixtures/` — `.py` script fixtures: good (`good_ansa_script.py`, `ex_*`), bad (`no_import.py`, `no_main.py`, `syntax_error.py`, `gui_script.py`)

### `skill_tests/` — protocol acceptance test cases (not pytest)
- `skill_tests/execution_test_cases_v1.md` — Phase 1 acceptance test cases EX-01..EX-09

## Requirements

- BETA CAE ANSA v25.0.0 installed
- `sim-cli` with the ANSA driver
- For integration tests: a valid ANSA license
