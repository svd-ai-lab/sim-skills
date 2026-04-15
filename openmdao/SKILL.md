---
name: openmdao-sim
description: Use when driving OpenMDAO (NASA's open-source multidisciplinary design, analysis, and optimization framework) via Python scripts — coupled systems with MDA, gradient-based / gradient-free optimization, derivative computation, surrogate models — through sim runtime one-shot execution.
---

# openmdao-sim

You are connected to **OpenMDAO** via sim-cli.

OpenMDAO is the canonical open-source MDAO framework, originally from
NASA Glenn. Pure Python (numpy, scipy, networkx). Pip-installable
(`pip install openmdao`).

Scripts are plain `.py`:

```python
import openmdao.api as om

prob = om.Problem()
prob.model.add_subsystem('comp', MyComp(), promotes=['*'])
prob.driver = om.ScipyOptimizeDriver()
prob.model.add_design_var('x', lower=-10, upper=10)
prob.model.add_objective('y')
prob.setup()
prob.run_driver()
print(prob['x'], prob['y'])
```

Same subprocess driver mode as PyBaMM / SfePy / Cantera.

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/workflow.md` | Problem → model → components → solvers/drivers → setup → run. |
| `base/reference/components.md` | ExplicitComponent, ImplicitComponent, ExecComp, IndepVarComp. |
| `base/reference/solvers.md` | NonlinearBlockGS, NewtonSolver, DirectSolver, LinearBlockGS. |
| `base/reference/optimization.md` | ScipyOptimizeDriver, design vars / objective / constraints. |
| `base/snippets/01_sellar.py` | Verified Sellar coupled MDA E2E. |
| `base/known_issues.md` | Cyclic groups need NL solver, set_input_defaults vs setup. |

## sdk/3/ — OpenMDAO 3.x

- `sdk/3/notes.md` — version-specific surface notes.

---

## Hard constraints

1. **Cyclic groups MUST set a nonlinear solver.** Sellar-style
   coupled disciplines (D1 → D2 → D1) need
   `group.nonlinear_solver = om.NonlinearBlockGS()` (or NewtonSolver).
   Without it the residual loop is open and `run_model()` errors.
2. **`setup()` is mandatory before `run_model()` or `run_driver()`.**
   It builds the data passing graph and allocates arrays.
3. **Use `set_input_defaults` for promoted inputs**, set after
   `add_subsystem` and before `setup`. Setting inputs *after* setup
   uses `prob['x'] = ...`.
4. **Acceptance != "ran without error"**. Always validate against a
   known reference (Sellar has y1=25.588 / y2=12.058 by convention;
   gradient-based runs should report objective improvement).
5. **Print results as JSON on the last stdout line.**

---

## Required protocol

1. Gather inputs:
   - **Category A:** disciplines / equations, design variables, objectives,
     constraints, acceptance criterion.
   - **Category B:** solver / driver tolerances, max iterations.
2. `sim check openmdao`.
3. Write `.py` per `base/reference/workflow.md`.
4. `sim lint script.py`.
5. `sim run script.py --solver openmdao`.
6. Validate JSON.
