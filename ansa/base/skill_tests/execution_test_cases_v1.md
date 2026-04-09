# Execution Test Cases v1 — ansa-sim

> **Status**: v1.1 — all tests PASS including real ANSA execution.
> **Last verified**: 2026-04-03, ANSA v25.0.0, sim-cli 0.2.0

---

## Test Fixtures

| ID | File | Type | Location |
|----|------|------|----------|
| FIX-1 | good_ansa_script.py | Valid ANSA script with main() | `tests/fixtures/` |
| FIX-2 | no_import.py | Python without `import ansa` | `tests/fixtures/` |
| FIX-3 | syntax_error.py | Broken Python syntax | `tests/fixtures/` |
| FIX-4 | no_main.py | ANSA script without main() | `tests/fixtures/` |
| FIX-5 | gui_script.py | ANSA script with GUI functions | `tests/fixtures/` |
| FIX-6 | ex_hello.py | Minimal batch smoke test | `tests/fixtures/` |
| FIX-7 | ex_create_mesh.py | Entity collection and property creation | `tests/fixtures/` |
| FIX-8 | ex_deck_info.py | Multi-deck capability query | `tests/fixtures/` |
| FIX-9 | ex_quality_check.py | Material + property creation cycle | `tests/fixtures/` |

---

## EX-01 — Connectivity Check

**Goal**: Verify `driver.connect()` detects ANSA v25.0.0.

**Acceptance criteria**:
| Field | Expected |
|-------|----------|
| `status` | `"ok"` |
| `version` | `"25.0.0"` |
| `message` | contains `"ansa64.bat"` |

---

## EX-02 — Script Detection

**Goal**: Verify `driver.detect()` correctly identifies ANSA scripts.

| Input | Expected |
|-------|----------|
| `.py` with `import ansa` | `True` |
| `.py` without `import ansa` | `False` |
| `.ansa` file | `True` |
| `.txt` file | `False` |
| Nonexistent file | `False` |

---

## EX-03 — Script Linting

**Goal**: Verify `driver.lint()` validates scripts correctly.

| Input | `ok` | Key diagnostic |
|-------|------|----------------|
| good_ansa_script.py | `True` | (none) |
| no_import.py | `False` | "No 'import ansa'" |
| syntax_error.py | `False` | "Syntax error" |
| no_main.py | `True` | Warning: "No main()" |
| gui_script.py | `True` | Warning: "requires GUI" |
| Empty .py | `False` | "Script is empty" |
| Empty .ansa | `False` | "file is empty" |
| Non-empty .ansa | `True` | (none) |

---

## EX-04 — Output Parsing

**Goal**: Verify `parse_output()` extracts JSON from stdout.

| Input | Expected |
|-------|----------|
| `""` | `{}` |
| `"no json"` | `{}` |
| `'{"count": 42}'` | `{"count": 42}` |
| Multi-line, last JSON wins | Last JSON object |

---

## EX-05 — Error Paths

| Scenario | Expected |
|----------|----------|
| ANSA not installed (mocked) | `RuntimeError` |
| `.ansa` file passed to run_file | `RuntimeError` with guidance |
| Unsupported extension | `RuntimeError` |

---

## EX-06 — Batch Execution: Smoke Test

**Goal**: Execute `ex_hello.py` — verify ANSA launches, imports work, JSON captured.

**Acceptance criteria**:
| Field | Expected |
|-------|----------|
| `exit_code` | `0` |
| `duration_s` | `> 0` (typically ~1.5s) |
| `solver` | `"ansa"` |
| `parsed.status` | `"ok"` |
| `parsed.deck` | `"NASTRAN"` |

---

## EX-07 — Entity Collection and Property Creation

**Goal**: Execute `ex_create_mesh.py` — verify CollectEntities and CreateEntity API work.

**Acceptance criteria**:
| Field | Expected |
|-------|----------|
| `exit_code` | `0` |
| `parsed.status` | `"ok"` |
| `parsed.property_created` | `true` |
| `parsed.props_after` | `≥ 1` |

---

## EX-08 — Multi-Deck Capability Query

**Goal**: Execute `ex_deck_info.py` — verify all solver decks are available.

**Acceptance criteria**:
| Field | Expected |
|-------|----------|
| `exit_code` | `0` |
| `parsed.status` | `"ok"` |
| `parsed.deck_count` | `≥ 7` |
| `parsed.decks_available` | includes `NASTRAN`, `ABAQUS`, `LSDYNA`, `FLUENT` |

---

## EX-09 — Material and Property Creation Cycle

**Goal**: Execute `ex_quality_check.py` — verify Create → Collect → Read cycle.

**Acceptance criteria**:
| Field | Expected |
|-------|----------|
| `exit_code` | `0` |
| `parsed.status` | `"ok"` |
| `parsed.mat_created` | `true` |
| `parsed.prop_created` | `true` |
| `parsed.thickness` | `1.0` |

---

## Test Result Summary (2026-04-03)

| Case | Status | Notes |
|------|--------|-------|
| EX-01 | **PASS** | `status=ok, version=25.0.0` |
| EX-02 | **PASS** | All 5 detection cases correct |
| EX-03 | **PASS** | All 8 lint cases correct |
| EX-04 | **PASS** | All 5 parsing cases correct |
| EX-05 | **PASS** | All 3 error paths raise correctly |
| EX-06 | **PASS** | exit=0, 1.52s, JSON parsed correctly |
| EX-07 | **PASS** | exit=0, 1.45s, property created |
| EX-08 | **PASS** | exit=0, 1.56s, 7 decks available |
| EX-09 | **PASS** | exit=0, 1.44s, material + property + thickness readback |

**31 pytest tests passed** + **4 real ANSA execution tests passed**.

## License Resolution

**Root cause**: `ansa64.bat` sets `ANSA_SRV=ansa_srv.localdomain` (unresolvable default).
With SSQ-patched exe, `ANSA_SRV=localhost` is required.

**Fix applied in driver**: `_run_python()` generates a wrapper `.bat` that:
1. Sets `ANSA_SRV=localhost` (if not already defined)
2. Sets all required environment variables with quoted paths
3. Calls `ansa_win64.exe` directly (bypasses `ansa64.bat` path-quoting issues)

This avoids the `ansa64.bat` bug where `ANSA_EXEC_DIR=%~dp0` breaks in paths with spaces.
