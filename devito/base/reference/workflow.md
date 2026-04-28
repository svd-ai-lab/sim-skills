# Devito workflow

```python
from devito import Grid, Function, TimeFunction, Eq, solve, Operator, Constant

# 1. Grid (shape in cells, extent in physical units)
grid = Grid(shape=(100, 100), extent=(1.0, 1.0))   # 2D unit square

# 2. Functions
# - Function: static (e.g., velocity model)
m   = Function(name='m', grid=grid)                # 1/v^2 for wave
# - TimeFunction: time-dependent (e.g., wavefield)
u   = TimeFunction(name='u', grid=grid,
                   time_order=2, space_order=4)    # 2nd-order in t, 4th in x

# 3. Initial / boundary conditions (numpy interface)
import numpy as np
m.data[:] = 1.0
u.data[0, 50, 50] = 1.0     # delta source at center

# 4. Symbolic PDE (using SymPy operators)
# acoustic wave: m * d2u/dt2 = laplace(u)
pde     = m * u.dt2 - u.laplace
stencil = Eq(u.forward, solve(pde, u.forward))

# 5. Operator (compiles to optimized C on first apply)
op = Operator([stencil])

# 6. Run
op.apply(time_M=200, dt=0.001)        # 200 time steps

# 7. Read out (last time slot)
final = u.data[-1]
print(final.max(), final.shape)
```

## Always emit JSON

```python
import json
print(json.dumps({
    "ok": True,
    "u_max": float(u.data[-1].max()),
    "u_l2":  float((u.data[-1] ** 2).sum() ** 0.5),
}))
```
