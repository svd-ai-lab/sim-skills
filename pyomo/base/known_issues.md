# Known Issues — Pyomo Driver

## Pyomo is NOT a solver

**Status**: Architecture
**Description**: `pip install pyomo` only gives the modeling layer.
A backend solver must be installed separately. For pure-pip:
`pip install highspy` then use `SolverFactory('appsi_highs')`.

## SolverFactory always returns a solver object

**Status**: API quirk
**Description**: `pyo.SolverFactory('nonexistent')` does NOT raise — it
returns an unavailable solver. Always check
`solver.available(exception_flag=False)` before `.solve()`.

## ConcreteModel vs AbstractModel

**Status**: API design
**Description**: `ConcreteModel` is built with data inline, ready to
solve. `AbstractModel` is a template requiring `.create_instance(data)`.
For 95% of scripts, use `ConcreteModel`.

## Indexed Var declaration order matters

**Status**: API quirk
**Description**: When declaring `m.x = pyo.Var(m.I, ...)`, the index
set `m.I` must be added to the model BEFORE `m.x`.

## Solution status check

**Status**: Convention
**Description**: After `result = solver.solve(m)`, check:
```python
from pyomo.opt import SolverStatus, TerminationCondition
assert result.solver.status == SolverStatus.ok
assert result.solver.termination_condition == TerminationCondition.optimal
```
Don't trust `pyo.value(m.obj)` blindly if status isn't `ok`.

## Chinese locale logging issue

**Status**: Cosmetic
**Description**: HiGHS logs in stdout. To silence: `solver.solve(m, tee=False)`
(default) or redirect via the solver's own log_level config.

## Units (pint) integration

**Status**: Optional
**Description**: Pyomo has a units extension (`pyomo.environ.units`).
Useful for engineering models, but not required.
