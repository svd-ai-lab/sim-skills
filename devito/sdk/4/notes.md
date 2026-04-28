# Devito 4.x Notes

## Provenance

- Source: PyPI `devito`
- Verified version: 4.8.6
- Pure-Python frontend + JIT-compiled C kernels
- Runtime requires gcc/clang on PATH

## Capabilities verified

| Feature | Status | Notes |
|---------|--------|-------|
| `Grid(shape, extent)` | Verified | 2D unit square |
| `TimeFunction(time_order, space_order)` | Verified | 1st/2nd order |
| `Eq`, `solve(...)` | Verified | symbolic |
| `Operator([stencil]).apply(time_M, dt)` | Verified | JIT compile + run |
| `u.data[t]` numpy access | Verified | read & write |

## 2D heat-diffusion benchmark

20x20 grid, point source 100, α=0.1, 20 steps, dt=0.001:
peak: 12.5 (sensible decay)
mass conservation: 4e-7 relative error (machine precision)

## Version detection

```bash
python3 -c "import devito; print(devito.__version__)"
```
returns `4.8.6`. Driver normalizes to `4.8`.

## Dependencies pulled in

The wheel installs: numpy, scipy, sympy, cgen, codepy, pytools, click,
multidict. Plus depends on a system C compiler being installed
separately.
