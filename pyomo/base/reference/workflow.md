# Pyomo workflow

```python
import pyomo.environ as pyo

# 1. Create model (Concrete = data fixed at build; Abstract = template)
m = pyo.ConcreteModel()

# 2. Sets
m.I = pyo.Set(initialize=[1, 2, 3])

# 3. Parameters
m.cost = pyo.Param(m.I, initialize={1: 1.0, 2: 2.5, 3: 0.7})

# 4. Variables (with domain)
m.x = pyo.Var(m.I, within=pyo.NonNegativeReals)
m.y = pyo.Var(within=pyo.Binary)

# 5. Objective
m.obj = pyo.Objective(
    expr=sum(m.cost[i] * m.x[i] for i in m.I),
    sense=pyo.minimize,
)

# 6. Constraints
m.c1 = pyo.Constraint(expr=sum(m.x[i] for i in m.I) >= 1.0)
def _logic_rule(m):
    return m.x[1] + m.x[2] <= 5 * m.y
m.c2 = pyo.Constraint(rule=_logic_rule)

# 7. Solve (backend solver MUST be installed)
solver = pyo.SolverFactory('appsi_highs')   # or 'glpk', 'cbc', 'ipopt'
result = solver.solve(m, tee=False)

# 8. Read solution
for i in m.I:
    print(i, pyo.value(m.x[i]))
print('obj', pyo.value(m.obj))
```

## Always emit JSON

```python
import json
print(json.dumps({
    "ok": True,
    "obj": float(pyo.value(m.obj)),
    "x": {str(i): float(pyo.value(m.x[i])) for i in m.I},
}))
```
