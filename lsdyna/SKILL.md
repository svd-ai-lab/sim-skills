---
name: lsdyna-sim
description: "Use when running Ansys LS-DYNA explicit/implicit FEA simulations — .k keyword file creation, lsdyna batch execution, d3plot result verification, convergence analysis"
---

# LS-DYNA Skill

## Identity

| Field | Value |
|---|---|
| Solver | Ansys LS-DYNA (explicit/implicit nonlinear FEA) |
| Execution | One-shot subprocess: `lsdyna_sp.exe i=<file.k>` |
| Session | **No** (`supports_session = False`) — one-shot only |
| SDK | None — pure command-line execution |
| Script language | LS-DYNA keyword format (`.k` / `.key` / `.dyn`) |
| Post-processing | LS-PrePost (GUI), or d3hsp/glstat text parsing |

## Scope

- **In scope**: Running LS-DYNA simulations via `.k` keyword files, keyword file validation, convergence verification, output parsing (d3hsp, glstat, messag), explicit and implicit dynamics
- **Out of scope**: Mesh generation (use ANSA, ICEM, or Workbench Meshing), geometry creation, LS-PrePost automation (GUI-only, no batch API), MPP parallel execution setup

## Hard constraints

1. **`*KEYWORD` must be the first line**: Every `.k` file must begin with `*KEYWORD`. Files without this marker are rejected.
2. **`*END` must terminate the file**: Missing `*END` causes unpredictable parsing behavior.
3. **Fixed-width card format**: LS-DYNA uses 8-character or 10-character fixed-width fields. Misaligned data is silently misread — never use free-format unless the keyword explicitly supports it.
4. **`exit_code == 0` does not mean success**: LS-DYNA returns exit code 0 even on error termination. Always check for `N o r m a l    t e r m i n a t i o n` in output (spaced characters).
5. **DLL dependencies on Windows**: The solver requires Intel runtime DLLs (libiomp5md.dll) from the ANSYS `tp/IntelCompiler/` tree. The driver handles this automatically via PATH augmentation.
6. **Output goes to files, not stdout**: Primary results go to `d3plot` (binary), `d3hsp` (text log), `glstat` (global stats), `messag` (log). Stdout contains only progress and termination status.

## Required protocol

### Step 0 — Check availability
```bash
sim check ls_dyna
```

### Step 1 — Validate inputs (Category A / B / C)
- **Category A** (must ask user): geometry/mesh (`.k` file), materials, boundary conditions, loads, acceptance criteria, termination time
- **Category B** (may default): precision (single/double), number of CPUs, memory allocation, timestep scale factor
- **Category C** (derive from files): element types, material model IDs, node/element counts

### Step 2 — Lint
```bash
sim lint <file.k>
```
Checks: `*KEYWORD` present, `*END` present, `*NODE`/`*ELEMENT` sections exist, `*CONTROL_TERMINATION` defined.

### Step 3 — Execute (one-shot)
```bash
sim run <file.k> --solver ls_dyna
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
- Check energy balance in `glstat` (total energy should be approximately conserved)
- Verify timestep didn't drop below `DTMIN`
- Check for excessive mass scaling if `DT2MS` is set

For implicit:
- Check convergence iterations in `d3hsp`
- Verify displacement convergence tolerance met

## Input file format

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

| Path | What | When to read |
|---|---|---|
| `base/reference/keyword_format.md` | Keyword file format and card layout | Writing or modifying .k files |
| `base/reference/material_models.md` | Common material model keywords | Choosing material models |
| `base/reference/control_cards.md` | Control card reference | Setting solver parameters |
| `base/reference/output_files.md` | Output file types and contents | Understanding solver results |
| `base/snippets/` | Example keyword files | Quick reference for common setups |
| `base/workflows/single_hex_tension/` | Single element E2E test case | Complete workflow example |
| `base/known_issues.md` | Known issues and workarounds | Debugging failures |
| `solver/14.0/notes.md` | LS-DYNA R14.0 (Ansys 2024 R1) notes | Version-specific behavior |
