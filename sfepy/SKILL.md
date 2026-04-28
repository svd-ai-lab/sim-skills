---
name: sfepy-sim
description: Use when driving SfePy (Simple Finite Elements in Python) — pure-Python FEM framework for PDE solving via direct API (Mesh / Field / Term / Problem) — through sim runtime one-shot execution. Covers Poisson / elasticity / Navier-Stokes / piezo / multi-physics weak forms.
---

# sfepy-sim

You are connected to **SfePy** via sim-cli.

SfePy is a pure-Python FEM toolkit (with NumPy/SciPy + small Cython
inner loops). Pip-installable (`pip install sfepy`). Two usage modes:

1. **Declarative problem-description files** run via `sfepy-run`
   (CLI scans `materials = {}`, `regions = {}`, `equations = {}` dicts).
2. **Direct API** — `from sfepy.discrete import Problem, ...`. This is
   the mode the driver uses (consistent with other Python solvers).

Scripts are plain `.py`:

```python
from sfepy.discrete.fem import FEDomain, Field
from sfepy.discrete import (
    FieldVariable, Material, Integral, Equation, Equations, Problem
)
from sfepy.terms import Term
from sfepy.discrete.conditions import Conditions, EssentialBC
from sfepy.solvers.ls import ScipyDirect
from sfepy.solvers.nls import Newton
```

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/workflow.md` | Mesh → domain/regions → field → variables → terms → equation → problem → solve. |
| `base/reference/terms.md` | Common weak-form terms (`dw_laplace`, `dw_lin_elastic`, `dw_volume_lvf`, ...). |
| `base/reference/regions.md` | Region selectors: `'all'`, `'vertices in (x < 0.001)'`, etc. |
| `base/snippets/01_poisson.py` | Verified Poisson E2E. |
| `base/known_issues.md` | API churn, `state.get_state_parts()`, region selector syntax. |

## sdk/2025/ — SfePy 2025.x

- `sdk/2025/notes.md` — version-specific API surface notes.

---

## Hard constraints

1. **The Term registry IS the API.** Don't write weak forms yourself —
   compose existing `Term.new('dw_xxx(args)', integral, region, ...)`
   from `sfepy.terms`. List of available terms is large; check
   `base/reference/terms.md`.
2. **Region selector syntax is restrictive.** Use the documented
   forms; arbitrary Python in selector strings is not parsed.
3. **Use `gen_block_mesh` for canonical box meshes** (`from sfepy.mesh.mesh_generators`).
   For complex geometry, build with Gmsh and read via meshio bridge.
4. **Acceptance != "ran without error"**. Always validate against an
   analytical or benchmark value (e.g. Poisson u_max ≈ 0.0737 on unit
   square with f=1).
5. **Print results as JSON on the last stdout line** for sim's
   `parse_output` to pick up.

---

## Required protocol

1. Gather inputs:
   - **Category A:** PDE, domain, BCs, polynomial order, acceptance.
   - **Category B:** mesh density, integration order, solver type.
2. `sim check sfepy` to confirm wheel is importable.
3. Write `.py` following `base/reference/workflow.md`.
4. `sim lint script.py`.
5. `sim run script.py --solver sfepy`.
6. Validate the final JSON against the acceptance criterion.
