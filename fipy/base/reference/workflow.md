# FiPy workflow

```python
from fipy import (
    CellVariable, FaceVariable,
    Grid1D, Grid2D, Grid3D,
    TransientTerm, DiffusionTerm, ConvectionTerm, ImplicitSourceTerm,
)

# 1. Mesh
mesh = Grid1D(nx=50, dx=0.02)
# or:  mesh = Grid2D(nx=40, ny=40, dx=0.025, dy=0.025)

# 2. Dependent variable + initial value
phi = CellVariable(name='phi', mesh=mesh, value=0.0)

# 3. Boundary conditions
phi.constrain(1.0, mesh.facesLeft)
phi.constrain(0.0, mesh.facesRight)
# Neumann (zero flux) is the natural BC — no constrain needed.
# Non-zero Neumann: use FaceVariable with .faceGrad.constrain(...)

# 4. Equation
D = 1.0   # diffusivity
eq = TransientTerm() == DiffusionTerm(coeff=D)
# or steady state:
# eq = DiffusionTerm(coeff=D) == 0
# or with source:
# eq = TransientTerm() == DiffusionTerm(coeff=D) - ImplicitSourceTerm(coeff=k)

# 5. Solve
# Steady: single solve
eq.solve(var=phi)
# Transient: time loop
dt = 0.5 * dx**2 / (2*D)         # CFL-like
for _ in range(100):
    eq.solve(var=phi, dt=dt)

# Nonlinear: sweep until residual converges
for sweep in range(10):
    res = eq.sweep(var=phi, dt=dt)
    if res < 1e-6: break

# 6. Read results (NumPy array via .value)
print(phi.value[mesh.numberOfCells // 2])
```

## Always emit JSON

```python
import json
print(json.dumps({
    "ok": True,
    "phi_mid": float(phi.value[mesh.numberOfCells // 2]),
}))
```
