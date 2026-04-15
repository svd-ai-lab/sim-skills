---
name: pymoo-sim
description: Use when driving pymoo (Multi-Objective Optimization in Python framework) via Python scripts — NSGA-II / NSGA-III / MOEA/D / R-NSGA / U-NSGA / single-obj GA / DE / PSO / CMAES — for benchmark problems and user-defined objective/constraint vectors, through sim runtime one-shot execution.
---

# pymoo-sim

You are connected to **pymoo** via sim-cli.

pymoo is the standard Python framework for multi-objective optimization
(Blank & Deb, 2020). Pip-installable (`pip install pymoo`); pure Python
+ numpy + scipy + autograd.

Scripts are plain `.py`:

```python
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.problems import get_problem
from pymoo.optimize import minimize

problem  = get_problem('zdt1')
res      = minimize(problem, NSGA2(pop_size=40), ('n_gen', 50), seed=1)
print(res.F)        # Pareto front objectives, shape (k, n_obj)
print(res.X)        # corresponding design vectors, shape (k, n_var)
```

Same subprocess driver mode as PyBaMM / PyMFEM / SfePy.

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/workflow.md` | Problem → algorithm → minimize → result. |
| `base/reference/algorithms.md` | NSGA2/3, MOEA/D, GA, DE, PSO, CMAES — when to pick what. |
| `base/reference/problems.md` | Built-in benchmarks vs user-defined ElementwiseProblem / Problem. |
| `base/reference/termination.md` | `('n_gen', N)`, `MaximumGenerationTermination`, etc. |
| `base/snippets/01_zdt1_nsga2.py` | Verified ZDT1 E2E. |
| `base/known_issues.md` | Python 3.7 incompat for 0.6.1+, seeded vs unseeded runs. |

## sdk/0/ — pymoo 0.6.x

- `sdk/0/notes.md` — version-specific surface notes.

---

## Hard constraints

1. **For multi-obj, Pareto front lives in `res.F` (shape (k, n_obj))**,
   design vectors in `res.X`. Single-objective: `res.F` is shape (1, 1)
   and `res.X` shape (1, n_var).
2. **Always pass a `seed` for reproducibility** when comparing runs.
3. **User-defined problems** subclass `ElementwiseProblem` (one solution
   evaluated per `_evaluate` call) or `Problem` (whole pop vectorized).
4. **Acceptance != "ran without error"**. Validate via:
   - hypervolume (HV) above threshold
   - Pareto front coverage (n_pareto >= N_min)
   - bounds on f1_min / f2_min for canonical problems (ZDT1: f1=0..1)
5. **Print results as JSON on the last stdout line.**

---

## Required protocol

1. Gather inputs:
   - **Category A:** objective(s), constraints, design var bounds,
     algorithm choice, termination, acceptance.
   - **Category B:** population size, seed, mutation/crossover params.
2. `sim check pymoo`.
3. Write `.py` per `base/reference/workflow.md`.
4. `sim lint script.py`.
5. `sim run script.py --solver pymoo`.
6. Validate JSON.
