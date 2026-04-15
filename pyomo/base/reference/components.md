# Pyomo components

| Component | Purpose | Example |
|---|---|---|
| `Set` | index set | `m.I = pyo.Set(initialize=[1,2,3])` |
| `RangeSet` | integer range | `m.T = pyo.RangeSet(1, 24)` |
| `Param` | constant data | `m.c = pyo.Param(m.I, initialize={1:1, 2:2})` |
| `Var` | decision variable | `m.x = pyo.Var(m.I, within=pyo.Reals)` |
| `Objective` | scalar to optimize | `m.obj = pyo.Objective(expr=..., sense=pyo.minimize)` |
| `Constraint` | equality / inequality | `m.c = pyo.Constraint(expr=m.x[1] >= 1)` |
| `ConstraintList` | indexed group | `m.cs.add(...)` per iter |
| `Expression` | named reusable expr | `m.profit = pyo.Expression(expr=...)` |

## Variable domains

| Domain | Values |
|---|---|
| `Reals` | (-inf, inf) |
| `NonNegativeReals` | [0, inf) |
| `NonPositiveReals` | (-inf, 0] |
| `Integers` | all integers |
| `NonNegativeIntegers` | 0, 1, 2, ... |
| `Binary` | {0, 1} |

## Indexed declarations via rule functions

```python
def _cap_rule(m, t):
    return m.x[t] <= m.cap[t]
m.cap_con = pyo.Constraint(m.T, rule=_cap_rule)
```
