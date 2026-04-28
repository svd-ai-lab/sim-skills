# PDE terms

| Term | Continuous form | When to use |
|---|---|---|
| `TransientTerm()` | ∂φ/∂t | put on LHS of any time-stepping equation |
| `DiffusionTerm(coeff=D)` | ∇·(D ∇φ) | diffusion / heat / Laplace |
| `ConvectionTerm(coeff=u)` | ∇·(u φ) | advection (u is FaceVariable!) |
| `ImplicitSourceTerm(coeff=k)` | k φ (linearized) | linear reaction sink |
| `ExplicitDiffusionTerm(coeff=D)` | ∇·(D ∇φ) explicit | for explicit time stepping |

Source terms that are not proportional to φ go on the **RHS** as a
constant (CellVariable):

```python
S = CellVariable(mesh=mesh, value=1.0)
eq = TransientTerm() == DiffusionTerm(coeff=D) + S
```

## Nonlinear terms

DiffusionTerm coefficient may be a function of `phi`:

```python
D = 1.0 + phi**2
eq = DiffusionTerm(coeff=D) == 0
# Use sweep, not solve, because D depends on the unknown
for _ in range(10):
    res = eq.sweep(var=phi)
    if res < 1e-6: break
```

## Convection scheme

Default is exponential (deferred upwind). For pure upwind:
```python
from fipy import UpwindConvectionTerm
eq = TransientTerm() == DiffusionTerm(coeff=D) - UpwindConvectionTerm(coeff=u)
```
