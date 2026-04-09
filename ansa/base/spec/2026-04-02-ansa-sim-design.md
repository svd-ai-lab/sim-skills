# ansa-sim Design Spec

**Date**: 2026-04-02  
**Scope**: Phase 1 — batch script execution via `ansa64.bat -execscript -nogui`  
**Status**: Active

---

## 1. What ANSA Is (and Isn't)

ANSA is a **CAE pre-processor**, not a solver. It prepares models for solvers:
- Import CAD geometry → clean up → mesh → assign properties → export solver deck

The agent's job: automate geometry cleanup, mesh generation, quality checking, and solver deck export. The agent does NOT run simulations — it prepares inputs for solvers (NASTRAN, ABAQUS, LS-DYNA, Fluent, etc.).

### Execution model

ANSA's Python API (`ansa` module) is **process-internal** — only available inside `ansa_win64.exe`. There is no external gRPC/COM/socket API. The only automation path is:

```
ansa64.bat -execscript "script.py|main()" -nogui
```

Each invocation is a fresh ANSA process. No persistent sessions across calls.

---

## 2. Execution Pipeline

```
lint .py → connect (check installed) → run_file → parse output → verify acceptance
```

Same one-shot model as PyBaMM. No `connect / exec / inspect / disconnect` loop.

```python
driver = AnsaDriver()
driver.lint(script)         # validate Python syntax + ansa import
driver.connect()            # check ANSA installation
result = driver.run_file(script)  # batch execute, blocks until done
data = driver.parse_output(result.stdout)  # extract JSON result
```

---

## 3. Scope

### In scope
- Running `.py` scripts that `import ansa` in batch mode (`-nogui`)
- Validating scripts before running (syntax, import, main() convention)
- Checking ANSA installation
- Capturing stdout/stderr from ANSA process
- Parsing JSON output from scripts

### Out of scope
- Persistent sessions (ANSA has no external API)
- GUI automation (no `pywinauto` path planned)
- Direct `.ansa` database manipulation (requires ANSA process)
- Solver execution (ANSA is a pre-processor, not a solver)

---

## 4. Agent Workflow

### Step 0 — Identify task type
Is this a meshing/pre-processing task? Does the user have an ANSA script? → Load Template 1.

### Step 1 — Validate inputs
- Script file exists
- `driver.lint()` returns `ok=True` (syntax OK, `import ansa` present)
- `driver.connect()` returns `status="ok"` (ANSA installed)

### Step 2 — Run
```python
result = driver.run_file(script)
```
Blocks until ANSA finishes. Typical runtime: 10s–10min depending on model complexity.

### Step 3 — Evaluate
1. `exit_code == 0` — ANSA did not crash
2. `stderr` empty or warnings only
3. `stdout` contains expected output (JSON result from script)
4. Acceptance criterion met (e.g., mesh quality > threshold)

### Step 4 — Report
Always report: exit_code, duration_s, extracted values, stderr if non-empty.

---

## 5. File Formats

| Extension | Type | detect() | lint() | run_file() |
|-----------|------|----------|--------|------------|
| `.py` | ANSA Python script | Yes (if `import ansa`) | Yes (AST + semantic) | Yes (`-execscript`) |
| `.ansa` | ANSA database | Yes | Yes (file check) | No (not executable) |
| `.nas`, `.bdf` | NASTRAN | No | No | No |
| `.inp` | ABAQUS | No | No | No |
| `.k` | LS-DYNA | No | No | No |

---

## 6. Known Constraints

1. **License required** — ANSA needs a valid license server (`ANSA_SRV`). Without it, ANSA shows a Launcher/license dialog and hangs.

2. **Large startup overhead** — ANSA takes 5-15 seconds to launch per invocation. No way to amortize this across multiple calls.

3. **No mid-run inspection** — Once a script starts, there's no way to query or interrupt it. The script must be self-contained.

4. **GUI functions fail in `-nogui`** — `PickEntities`, `guitk` dialogs, etc. won't work. The linter warns about these.

5. **Output encoding** — ANSA may produce non-UTF-8 output on Windows. The driver handles encoding errors.
