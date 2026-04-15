---
name: pyomo-sim
description: Use when driving Pyomo (Python-based open-source modeling language for mathematical optimization, Sandia/SNL) via Python scripts — LP / MIP / NLP / MINLP / SDP / DAE problems with backend solvers (HiGHS / GLPK / CBC / IPOPT / Gurobi / CPLEX) — through sim runtime one-shot execution.
---

# pyomo-sim

You are connected to **Pyomo** via sim-cli.

Pyomo is the canonical Python optimization modeling language (Sandia
National Labs). Pip-installable (`pip install pyomo`); pure Python
frontend that dispatches to backend solvers — Pyomo itself does
**not** solve, it builds the model and writes problem files.

Scripts are plain `.py`:

```python
import pyomo.environ as pyo
m = pyo.ConcreteModel()
m.x = pyo.Var(within=pyo.NonNegativeReals)
m.obj = pyo.Objective(expr=2*m.x, sense=pyo.minimize)
m.c = pyo.Constraint(expr=m.x >= 1)
pyo.SolverFactory('appsi_highs').solve(m)
print(pyo.value(m.x))
```

Same subprocess driver mode as PyBaMM / PyMFEM / SfePy.

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/workflow.md` | ConcreteModel → Vars/Params/Sets → Objective/Constraint → Solver → solve. |
| `base/reference/components.md` | Var, Param, Set, RangeSet, Objective, Constraint, Expression. |
| `base/reference/solvers.md` | HiGHS, GLPK, CBC, IPOPT, Gurobi, CPLEX — pick by problem class. |
| `base/snippets/01_lp_classic.py` | Verified LP E2E (textbook 3x+5y problem). |
| `base/known_issues.md` | Solver discovery, units, AbstractModel vs ConcreteModel. |

## sdk/6/ — Pyomo 6.x

- `sdk/6/notes.md` — version-specific surface notes.

---

## Hard constraints

1. **Pyomo is NOT a solver.** `SolverFactory(name).solve(m)` requires
   the named backend (`highspy`, `glpsol`, `cbc`, `ipopt`, ...) to be
   installed separately. `appsi_highs` ships via `pip install highspy`
   — easiest pure-pip path. Without a backend, models build but never
   produce solutions.
2. **`ConcreteModel` for normal scripts**, `AbstractModel` only when
   building a model template separated from data (legacy AMPL-style).
3. **Variables must declare a `within` domain** (Reals, NonNegativeReals,
   Integers, Binary, ...) for solver compatibility.
4. **Acceptance != "ran without error"**. Always check
   `solver.solve(m)` returns SolverStatus.ok and the result is feasible
   — and validate against an analytical or expected optimum.
5. **Print results as JSON on the last stdout line.**

---

## Required protocol

1. Gather inputs:
   - **Category A:** decision variables + bounds, objective, constraints,
     solver choice, acceptance criterion.
   - **Category B:** solver tolerances, time limits, threads.
2. `sim check pyomo` — confirms Pyomo + a usable backend.
3. Write `.py` per `base/reference/workflow.md`.
4. `sim lint script.py`.
5. `sim run script.py --solver pyomo`.
6. Validate JSON.
