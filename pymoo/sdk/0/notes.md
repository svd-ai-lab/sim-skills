# pymoo 0.6.x Notes

## Provenance

- Source: PyPI `pymoo`
- Verified version: 0.6.0 (3.7-compatible)
- Pure Python + numpy + scipy + autograd + cma

## Capabilities verified

| Feature | Status | Notes |
|---------|--------|-------|
| `get_problem('zdt1')` | Verified | bundled benchmark |
| `NSGA2(pop_size=40)` | Verified | |
| `minimize(problem, algo, ('n_gen', 50), seed=1)` | Verified | |
| `res.F`, `res.X` | Verified | shape (k, n_obj) / (k, n_var) |

## ZDT1 benchmark

NSGA-II 40-pop / 50-gen / seed=1 → 36 Pareto solutions,
f1_min ≈ 8.4e-5 (front passes through f1=0 ✓), f2_min ≈ 0.122.

## Version detection

```bash
python3 -c "import pymoo; print(pymoo.__version__)"
```
returns `0.6.0`. Driver normalizes to `0.6`.

## API differences vs 0.5.x (legacy)

- 0.5.x used `from pymoo.factory import get_algorithm` for everything
- 0.6.x uses direct imports: `from pymoo.algorithms.moo.nsga2 import NSGA2`
- Result attributes (`res.F`, `res.X`, `res.G`) unchanged across 0.5 → 0.6
