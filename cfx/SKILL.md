---
name: cfx-sim
description: "Use when creating, running, or debugging Ansys CFX simulations — CCL setup, cfx5solve batch execution, cfx5post visualization, convergence analysis, parameterized studies via Power Syntax"
---

# CFX Skill

## Identity

| Field | Value |
|---|---|
| Solver | Ansys CFX (turbomachinery / general-purpose CFD) |
| Execution | CLI subprocess: `cfx5solve -batch -def <file>` |
| Session | **Persistent** (`supports_session = True`) — interactive post-processing via `cfx5post -line` |
| SDK | None — pure command-line tools + Perl Power Syntax |
| Script language | CCL (CFX Command Language) — declarative physics definitions |
| Post-processing | Interactive: `cfx5post -line <results.res>` / Batch: `cfx5post -batch <session.cse>` |

## Scope

- **In scope**: Running CFX simulations via `.def` files, CCL configuration, post-processing with CFD-Post, convergence analysis, monitor data export, parametric studies via Power Syntax
- **Out of scope**: Mesh generation (use ICEM CFD or Workbench Meshing), geometry creation, Fluent cases (different solver, different driver)

## Hard constraints

1. **CCL is declarative, not imperative**: CCL defines WHAT the simulation is, not HOW to run it. Do not write control flow in CCL (use Power Syntax/Perl for that).
2. **A `.def` file is required for solving**: `.ccl` alone cannot be solved — it must be paired with a `.def` that contains the mesh. Use `cfx5cmds -write` to inject CCL into a `.def`.
3. **`cfx5cmds` cannot change mesh topology**: Only physics parameters (BCs, solver settings, materials) can be modified via `cfx5cmds -write`. Geometry/mesh changes require cfx5pre.
4. **Post-processing requires `.cse` session files**: `cfx5post -batch` needs a session file — it cannot accept raw CCL commands. Use `Colour Variable` (not `Variable`) for contours.
5. **Residual convergence alone does not validate physics**: All RMS residuals below target means numerical convergence, but physical correctness requires checking conservation quantities (mass imbalance, forces, monitor points).

## Required protocol

### Step 0 — Check availability
```bash
sim check cfx
```

### Step 1 — Validate inputs (Category A / B / C)
- **Category A** (must ask user): geometry/mesh (.def file), boundary conditions, materials, turbulence model, acceptance criteria
- **Category B** (may default): precision (single/double), max iterations, parallel cores
- **Category C** (derive from files): CCL version, domain names, boundary names

### Step 2 — Lint
```bash
sim lint <file.ccl>
```

### Step 3 — Execute (one-shot mode)
```bash
sim run <file.def> --solver cfx
```

### Step 4 — Interactive post-processing (session mode)

Session mode provides step-by-step feedback after solving:

```bash
# Connect with existing results
sim connect --solver cfx   # pass res_file= to load results

# Query boundaries and variables
sim inspect session.boundaries
sim inspect session.variables

# Evaluate quantities with instant feedback
sim exec "evaluate(massFlow()@inlet)"         # → 1.379 [kg s^-1]
sim exec "evaluate(areaAve(Pressure)@outlet)" # → -0.058 [Pa]
sim exec "evaluate(maxVal(Velocity)@Default Domain)"

# Create contour visualization
sim exec "CONTOUR: P\n  Colour Variable = Pressure\n  Location List = Default Domain Default\nEND"

# Export image
sim exec "HARDCOPY:\n  Hardcopy Filename = result.png\n  Hardcopy Format = png\nEND\n>print"

# Disconnect
sim disconnect
```

**Three-phase architecture:**
1. `cfx5solve -batch` — non-interactive solve
2. `cfx5post -line` — interactive post-processing (CCL + Perl evaluate)
3. Agent sends commands → gets quantitative feedback per step

### Step 5 — Verify convergence
Check the `.out` log or use session queries:
- `evaluate(massFlow()@inlet)` vs `evaluate(massFlow()@outlet)` — mass conservation
- All RMS residuals below target in `.out` file
- Monitor points stabilized

## File index

| Path | What | When to read |
|---|---|---|
| `base/reference/ccl_language.md` | CCL syntax reference | Writing or modifying CCL files |
| `base/reference/cli_tools.md` | Command-line tools reference | Running cfx5solve/pre/post/cmds |
| `base/reference/boundary_conditions.md` | BC types and CCL patterns | Setting up boundary conditions |
| `base/reference/solver_control.md` | Convergence settings guide | Tuning solver performance |
| `base/reference/post_processing.md` | CFD-Post session file guide | Creating visualization scripts |
| `base/reference/session_workflow.md` | Session 交互协议 + hybrid 渲染机制 | 使用 sim exec 分步查询和出图 |
| `base/snippets/` | Ready-made CCL snippets | Quick reference for common setups |
| `base/workflows/vmfl015/` | VMFL015 verification case E2E | Complete workflow example |
| `base/known_issues.md` | Known issues and workarounds | Debugging failures |
| `solver/24.1/notes.md` | Version 24.1 specific notes | Working with Ansys 2024 R1 |
