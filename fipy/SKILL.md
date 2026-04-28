---
name: fipy-sim
description: Use when driving FiPy (NIST's pure-Python finite-volume PDE solver) via Python scripts — diffusion / transient / convection / reaction PDEs on 1D/2D/3D structured / Gmsh meshes, steady or time-stepping — through sim runtime one-shot execution.
---

# fipy-sim

You are connected to **FiPy** via sim-cli.

FiPy is the canonical pure-Python finite-volume PDE solver (NIST,
2003-present). Pip-installable (`pip install fipy`); pure Python on top
of NumPy/SciPy with optional acceleration via PySparse / PyAMG /
petsc4py / Trilinos.

Scripts are plain `.py`:

```python
from fipy import CellVariable, Grid1D, TransientTerm, DiffusionTerm
mesh = Grid1D(nx=50, dx=0.02)
phi = CellVariable(name='phi', mesh=mesh, value=0.0)
phi.constrain(1.0, mesh.facesLeft)
phi.constrain(0.0, mesh.facesRight)
eq = TransientTerm() == DiffusionTerm(coeff=1.0)
for _ in range(100):
    eq.solve(var=phi, dt=0.01)
```

Same subprocess driver mode as PyBaMM / PyMFEM / SfePy.

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/workflow.md` | Mesh → variable → BCs → equation → solve / sweep loop. |
| `base/reference/meshes.md` | Grid1D / Grid2D / Gmsh2D, FaceVariable / CellVariable. |
| `base/reference/terms.md` | TransientTerm / DiffusionTerm / ConvectionTerm / Source. |
| `base/snippets/01_poisson.py` | Verified steady-state 1D Poisson E2E. |
| `base/known_issues.md` | Cell-center vs face values, sweep vs solve, sparse solver fallback. |

## sdk/4/ — FiPy 4.x

- `sdk/4/notes.md` — version-specific surface notes.

---

## Hard constraints

1. **Boundary conditions are applied via `.constrain(value, faces)`**,
   not by zeroing rows. `mesh.facesLeft / facesRight / facesTop / facesBottom`
   are the standard locators for grid meshes.
2. **For transient problems, use `TransientTerm()` on the LHS**:
   `TransientTerm() == DiffusionTerm(...)`. Without it, FiPy treats
   the equation as steady and ignores `dt`.
3. **For nonlinear equations, use `.sweep(var=, dt=)` in a loop until
   residual converges**, not `.solve` (which does one Newton step only).
4. **Acceptance != "ran without error"**. Always validate against an
   analytical or benchmark profile (e.g. linear profile for 1D Poisson
   with mixed Dirichlet, error function for 1D semi-infinite diffusion).
5. **Print results as JSON on the last stdout line.**

---

## Required protocol

1. Gather inputs:
   - **Category A:** PDE, domain, BCs, time span (transient), acceptance.
   - **Category B:** mesh density, time step, solver tolerance.
2. `sim check fipy`.
3. Write `.py` per `base/reference/workflow.md`.
4. `sim lint script.py`.
5. `sim run script.py --solver fipy`.
6. Validate JSON.
