# FiPy 4.x Notes

## Provenance

- Source: PyPI `fipy`
- Verified version: 4.0.2
- Pure Python + NumPy/SciPy + (optional) PySparse/PyAMG/petsc4py

## Capabilities verified

| Feature | Status | Notes |
|---------|--------|-------|
| `Grid1D` | Verified | with .facesLeft / .facesRight |
| `CellVariable` + `.constrain(...)` | Verified | Dirichlet BC |
| `DiffusionTerm(coeff=D)` | Verified | steady |
| `eq.solve(var=phi)` | Verified | machine-precision |

## 1D Poisson benchmark

50-cell grid, phi(0)=1, phi(1)=0 → mid = 0.49 (analytical 0.49,
error 1.6e-15). Linear, exact for diffusion-only equation.

## Version detection

```bash
python3 -c "import fipy; print(fipy.__version__)"
```
returns `4.0.2`. Driver normalizes to `4.0`.

## Dependencies pulled in

The wheel installs: numpy, scipy, future, click, typer, shellingham.
~50 MB total.
