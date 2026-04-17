# ANSA sim Driver — Final Report

> Date: 2026-04-04
> Result: **54/54 tests passing**, full STEP→mesh→export pipeline verified

---

## What Was Built

A complete ANSA pre-processor driver for sim, supporting two execution models:

| Mode | Mechanism | Use Case |
|------|-----------|----------|
| **Phase 1: One-shot batch** | `ansa_win64.exe -execscript -nogui` | Independent scripts, CI/CD |
| **Phase 2: IAP persistent session** | `-listenport` + TCP socket protocol | Interactive workflows, multi-step pipelines |

## Key Achievement: STEP → Mesh → Export Pipeline

```
screw.step (89KB, OpenCASCADE)
    ↓ base.Open()           → 10 FACE, 1 ANSAPART         (1.2s)
    ↓ mesh.Mesh(faces)      → 1,947 shells, 1,915 grids   (0.2s)
    ↓ CalculateOffElements  → 0 quality violations         (<0.1s)
    ↓ CreateEntity(MAT1)    → Steel 4140, E=210 GPa        (<0.1s)
    ↓ OutputNastran()       → 209 KB .nas, 878 KB .ansa    (0.1s)
```

**Total pipeline time: ~1.7 seconds** (excluding ANSA startup)

## Test Suite

```
54 tests passed in 14.79s
├── test_ansa_driver.py        31  Phase 1: detect/lint/connect/parse/run_file
├── test_runtime.py            12  Phase 2: IAP launch/exec/disconnect + state persistence
├── test_pipeline.py            5  Read Nastran → quality → modify → export
└── test_geometry_pipeline.py   6  STEP → mesh → quality → material → Nastran export
```

## Architecture

```
sim/src/sim/drivers/ansa/
├── __init__.py       Exports AnsaDriver, SessionInfo, RunRecord
├── driver.py         AnsaDriver class — Phase 1 (run_file) + Phase 2 (launch/run/disconnect)
├── schemas.py        SessionInfo + RunRecord dataclasses (Fluent pattern)
└── runtime.py        AnsaRuntime — IAP lifecycle manager
```

### Phase 1: One-shot

```python
driver = AnsaDriver()
result = driver.run_file(Path("script.py"))  # → RunResult
parsed = driver.parse_output(result.stdout)   # → dict
```

Launches `ansa_win64.exe -execscript "script.py|main()" -nogui`, captures stdout/stderr.

### Phase 2: IAP Session

```python
driver = AnsaDriver()
driver.launch()                    # Start ANSA with -listenport
result = driver.run(code)          # Execute snippet via IAP
result = driver.run_script(path)   # Execute file via IAP
driver.disconnect()                # goodbye + cleanup
```

Uses official BETA CAE Inter-ANSA Protocol (TCP socket, pure Python stdlib).

## Files Inventory

### Driver (sim core)

| File | Lines | Content |
|------|-------|---------|
| `drivers/ansa/driver.py` | 470 | DriverProtocol + IAP session methods |
| `drivers/ansa/runtime.py` | 240 | AnsaRuntime (launch/connect/exec/disconnect) |
| `drivers/ansa/schemas.py` | 60 | SessionInfo + RunRecord |
| `drivers/ansa/__init__.py` | 5 | Public exports |

### Agent (sim-agent-ansa)

| Directory | Content |
|-----------|---------|
| `skills/ansa-sim/SKILL.md` | Agent skill definition + API reference |
| `skills/ansa-sim/known_issues.md` | Resolved + open issues |
| `skills/ansa-sim/tests/` | Execution test cases v1 (EX-01 to EX-13) |
| `reference/ansa_api_reference.md` | Community-sourced API patterns |
| `reference/ANSA-Scripts/` | GitHub community scripts |
| `tests/test_ansa_driver.py` | 31 unit tests |
| `tests/test_runtime.py` | 12 IAP session tests |
| `tests/test_pipeline.py` | 5 Nastran read/modify/export tests |
| `tests/test_geometry_pipeline.py` | 6 STEP→mesh→export tests |
| `tests/fixtures/geometry/screw.step` | OpenCASCADE test geometry (89KB) |
| `tests/fixtures/geometry/input_plate.nas` | 5×5 plate Nastran model |
| `docs/` | Investigation + IAP test + runtime dev reports |

### Cookbook (sim-cookbook/ansa)

| File | Content |
|------|---------|
| `examples/nastran_plate_setup/README.md` | Cookbook with pipeline walkthrough |
| `screenshots/00_connect.png` | sim check ansa |
| `screenshots/01_materials.png` | Material properties comparison |
| `screenshots/02_properties.png` | Shell property thickness stack |
| `screenshots/03_deck_support.png` | 7 solver decks |
| `screenshots/04_test_results.png` | Test results + timing |
| `screenshots/05_pipeline.png` | sim→ANSA execution pipeline |
| `screenshots/06_geometry_pipeline.png` | STEP→mesh→export with real data |
| `screenshots/07_all_tests.png` | 54 tests breakdown |

## Bugs Fixed

| Bug | Root Cause | Fix |
|-----|-----------|-----|
| IAP hello() connection reset | `subprocess.Popen(stdout=PIPE)` blocks ANSA | `stdout=DEVNULL` |
| IAP timing race | Port opens before IAP protocol stack ready | 1s delay after `_wait_for_port` |
| IAP string_dict float error | IAP returns only `{str: str}` | All values wrapped in `str()` |

## Discoveries

1. **ANSA has official RemoteControl API** (IAP) — was previously unknown, thought to have no session capability
2. **`mesh.Mesh(faces)`** is the correct surface meshing API — accepts FACE entity list
3. **356 mesh functions** in `ansa.mesh` module (documented in official API stubs)
4. **`base.Open()`** handles STEP/IGES import automatically
5. **ANSA starts in ~2 seconds** in listener mode — fastest of all sim solver drivers

## Reproducibility

To reproduce the full test suite:

```bash
# Ensure ANSA v25.0.0 installed at E:\Program Files (x86)\ANSA\ansa_v25.0.0\

cd E:\sim\sim-agent-ansa
E:\sim\sim\.venv\Scripts\python.exe -m pytest tests/ -v
# Expected: 54 passed in ~15s
```
