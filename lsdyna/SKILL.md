---
name: lsdyna-sim
description: "Use when running Ansys LS-DYNA explicit/implicit FEA simulations — .k keyword file creation (hand-written or via PyDyna SDK), lsdyna batch execution, d3plot result verification, DPF post-processing"
---

# LS-DYNA Skill

## Identity

| Field | Value |
|---|---|
| Solver | Ansys LS-DYNA (explicit/implicit nonlinear FEA) |
| Execution | One-shot subprocess: `lsdyna_sp.exe i=<file.k>` |
| Session | **Yes** (`supports_session = True`) — Python namespace persists across `sim exec` (Deck builder + DPF Model). Solver itself remains one-shot inside the session. |
| SDK | `ansys-dyna-core` (PyDyna): `keywords` module for `.k` generation, `run` module for solver launch |
| Script language | LS-DYNA keyword format (`.k` / `.key` / `.dyn`), or Python via PyDyna |
| Post-processing | `ansys-dpf-core` (Python, recommended), or LS-PrePost (GUI) |

## Scope

- **In scope**: Running LS-DYNA simulations via `.k` keyword files, building decks
  via PyDyna `keywords` API, keyword file validation, convergence verification,
  output parsing (d3hsp, glstat, messag), explicit and implicit dynamics, DPF
  post-processing
- **Out of scope**: Mesh generation (use ANSA, ICEM, or Workbench Meshing),
  geometry creation, MPP parallel execution setup

## Hard constraints

1. **`*KEYWORD` must be the first line**: Every `.k` file must begin with
   `*KEYWORD`. Files without this marker are rejected.
2. **`*END` must terminate the file**: Missing `*END` causes unpredictable
   parsing behavior.
3. **Fixed-width card format (hand-written `.k`)**: LS-DYNA uses 8-character
   or 10-character fixed-width fields. Misaligned data is silently misread.
   **Use the PyDyna `keywords` API to avoid this entire class of bugs.**
4. **`exit_code == 0` does not mean success**: LS-DYNA returns exit code 0
   even on error termination. Always check for `N o r m a l    t e r m i n a t i o n`
   in output (spaced characters).
5. **DLL dependencies on Windows**: The solver requires Intel runtime DLLs
   (`libiomp5md.dll`) from the ANSYS `tp/IntelCompiler/` tree. The `sim`
   driver handles this automatically via PATH augmentation; PyDyna's
   `run_dyna()` assumes a properly set up ANSYS environment.
6. **Output goes to files, not stdout**: Primary results go to `d3plot`
   (binary), `d3hsp` (text log), `glstat` (global stats), `messag` (log).
   Stdout contains only progress and termination status.

## Dual-path strategy: hand-written `.k` vs PyDyna SDK

This skill supports **two interchangeable input paths**. Choose based on
the task:

| Path | When to use | Pros | Cons |
|------|-------------|------|------|
| **Hand-written `.k`** | Editing legacy decks, mesh files from ANSA/Workbench, quick smoke tests | Direct control, works without Python deps | KI-004 card alignment bugs, no IDE help |
| **PyDyna `keywords` API** | New deck construction, parametric studies, anything > 50 keywords | Type-safe, IDE autocomplete, automatic formatting, DataFrame-based bulk ops | Requires `pip install ansys-dyna-core` |

**Default recommendation**: For any new deck the agent builds from scratch,
use the PyDyna SDK path. For existing `.k` files the user provides, modify
in place (or load via `Deck.import_file()` and patch with PyDyna).

See:
- `base/reference/pydyna_keywords_api.md` for the full API reference
- `base/reference/pydyna_run_api.md` for `run_dyna()` usage
- `base/workflows/pydyna_taylor_bar/` for the canonical end-to-end example

## Execution modes

The driver supports both **one-shot** and **persistent session** modes:

### One-shot — `sim run file.k --solver ls_dyna`
- Direct subprocess call to `lsdyna_sp.exe i=file.k`
- Result stored as a numbered run in `.sim/runs/`
- Best for: pre-made `.k` files, CI smoke tests, batch processing

### Session — `sim connect --solver ls_dyna` then `sim exec` / `sim inspect`
- A Python namespace persists across calls, holding `deck`, `kwd`, `run_dyna`,
  `workdir`, `model`, `dpf`, etc.
- The solver call (`run_dyna(...)`) is still a one-shot subprocess inside,
  but the deck-building and DPF post-processing wrap around it interactively.
- Best for: incremental deck construction, parametric sweeps, DPF exploration.
- After any `sim exec` that produces a `d3plot`, the runtime auto-loads it
  into a `dpf.Model` so `sim inspect results.summary` works immediately.

See `base/reference/session_workflow.md` for the full session protocol,
inspect targets, and patterns.

## Required protocol

### Step 0 — Check availability
```bash
sim check ls_dyna
```

For PyDyna-path workflows, also verify:
```bash
python -c "from ansys.dyna.core import Deck, keywords; from ansys.dyna.core.run import run_dyna"
```

### Step 1 — Validate inputs (Category A / B / C)
- **Category A** (must ask user): geometry/mesh (`.k` file), materials,
  boundary conditions, loads, acceptance criteria, termination time
- **Category B** (may default): precision (single/double), number of CPUs,
  memory allocation, timestep scale factor
- **Category C** (derive from files): element types, material model IDs,
  node/element counts

### Step 2 — Build / lint the deck

**Path A (hand-written `.k`)**:
```bash
sim lint <file.k>
```
Checks: `*KEYWORD` present, `*END` present, `*NODE`/`*ELEMENT` sections
exist, `*CONTROL_TERMINATION` defined.

**Path B (PyDyna SDK)**:
```python
from ansys.dyna.core import Deck, keywords as kwd

deck = Deck()
deck.title = "..."
# ... add keywords ...
deck.export_file("input.k")
```
PyDyna validates types and field constraints at attribute-set time.

### Step 3 — Execute (one-shot)

**Path A (sim CLI)**:
```bash
sim run <file.k> --solver ls_dyna
```

**Path B (PyDyna `run_dyna`)**:
```python
from ansys.dyna.core.run import run_dyna
run_dyna("input.k", working_directory=wd)
```

### Step 4 — Verify results
Check for in the output:
- `N o r m a l    t e r m i n a t i o n` (spaced characters — mandatory)
- Problem cycle count matches expected range
- Problem time reached `*CONTROL_TERMINATION` endtime
- No `*** Error` or `*** Fatal` messages
- Output files produced: `d3plot`, `d3hsp`, `glstat`

### Step 5 — Physics validation
For explicit dynamics:
- Check energy balance in `glstat` (total energy should be approximately
  conserved)
- Verify timestep didn't drop below `DTMIN`
- Check for excessive mass scaling if `DT2MS` is set

For implicit:
- Check convergence iterations in `d3hsp`
- Verify displacement convergence tolerance met

### Step 6 — Post-process (recommended: DPF)

```python
import ansys.dpf.core as dpf

ds = dpf.DataSources()
ds.set_result_file_path("d3plot", "d3plot")
model = dpf.Model(ds)

# Global kinetic energy time series
gke_op = dpf.operators.result.global_kinetic_energy()
gke_op.inputs.data_sources.connect(ds)
ke = gke_op.eval().get_field(0).data

# Time axis
time = model.metadata.time_freq_support.time_frequencies.data_as_list
```

DPF can extract any field result without requiring LS-PrePost. See the
Taylor bar example for a full plot workflow.

## Input file format (hand-written reference)

### Keyword file structure
```
*KEYWORD
*TITLE
Description of the model
$
$ Comments start with $
$ Fixed-width cards: 8 characters per field (standard)
$
*CONTROL_TERMINATION
$  ENDTIM    ENDCYC     DTMIN    ENDENG    ENDMAS
   1.0e-3         0       0.0       0.0       0.0
*MAT_ELASTIC
$      MID        RO         E        PR
         1  7.85e-09    210000       0.3
*NODE
$    NID               X               Y               Z
       1       0.000000       0.000000       0.000000
*ELEMENT_SOLID
$    EID     PID      N1      N2      N3      N4      N5      N6      N7      N8
       1       1       1       2       3       4       5       6       7       8
*END
```

### Key rules
- All keywords start with `*` in column 1
- Data cards follow immediately after the keyword line
- Fields are right-justified within their 8-character columns
- Use `$` for comment lines
- `*INCLUDE` references external files

## File index

### Hand-written `.k` references
| Path | What | When to read |
|---|---|---|
| `base/reference/keyword_format.md` | Keyword file format and card layout | Writing or modifying .k files by hand |
| `base/reference/material_models.md` | Common material model keywords | Choosing material models |
| `base/reference/control_cards.md` | Control card reference | Setting solver parameters |
| `base/reference/output_files.md` | Output file types and contents | Understanding solver results |

### PyDyna SDK references
| Path | What | When to read |
|---|---|---|
| `base/reference/pydyna_install.md` | PyDyna installation, path config | Setting up a new project |
| `base/reference/pydyna_keywords_api.md` | `keywords` module — building `.k` programmatically | **Building decks in Python (preferred)** |
| `base/reference/pydyna_run_api.md` | `run_dyna()` solver launch | Running LS-DYNA from Python |
| `base/reference/pydyna_agent_integration.md` | PyDyna's bundled AI agent docs | Agent setup `--env claude --copy` |
| `base/reference/session_workflow.md` | **Session mode protocol** — connect/exec/inspect targets, patterns | Using `sim connect --solver ls_dyna` |

### Workflows
| Path | What | When to read |
|---|---|---|
| `base/snippets/01_single_hex_tension.k` | Hand-written single hex element | Quickest reference for explicit dynamics |
| `base/workflows/single_hex_tension/` | E2E test of the hand-written snippet | Verify driver pipeline |
| `base/workflows/pydyna_taylor_bar/` | **🌟 PyDyna end-to-end template** (impact + DPF) | Building any single-part impact problem |
| `base/workflows/pydyna_pendulum/` | Multi-rigid-body dynamics | Mechanism / linkage problems |
| `base/workflows/pydyna_pipe/` | Shell + self-contact | Thin-walled structures |
| `base/workflows/pydyna_buckling_beer_can/` | Nonlinear buckling | Imperfection-sensitive problems |
| `base/workflows/pydyna_optimization/` | Parametric sweep template | DOE / optimization studies |
| `base/workflows/pydyna_jupyter_plotting/` | Geometry preview in Jupyter | Notebook-based workflows |

### Other
| Path | What | When to read |
|---|---|---|
| `base/known_issues.md` | Known issues and workarounds | Debugging failures |
| `solver/14.0/notes.md` | LS-DYNA R14.0 (Ansys 2024 R1) notes | Version-specific behavior |
