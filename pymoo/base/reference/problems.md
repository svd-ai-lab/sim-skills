# Problems

## Built-in benchmarks

`get_problem(name)` returns a ready-to-use Problem instance.

| Family | Names | n_obj | Pareto front |
|---|---|---|---|
| ZDT | zdt1..zdt6 | 2 | convex (1, 4), concave (2, 3), discont (5, 6) |
| DTLZ | dtlz1..dtlz7 | scalable (default 3) | various (linear, concave, scaled) |
| WFG | wfg1..wfg9 | scalable | challenging (degenerate, biased) |
| CDTLZ / CTP | constrained variants | scalable | constrained Pareto |

## User-defined problem (vectorized)

```python
import numpy as np
from pymoo.core.problem import Problem

class MyProblem(Problem):
    def __init__(self):
        super().__init__(
            n_var=2, n_obj=2, xl=np.array([-2,-2]), xu=np.array([2,2]),
        )
    def _evaluate(self, X, out, *args, **kwargs):
        # X shape (n_pop, n_var); return F shape (n_pop, n_obj)
        out['F'] = np.column_stack([
            X[:,0]**2 + X[:,1]**2,
            (X[:,0]-1)**2 + X[:,1]**2,
        ])
```

Vectorized `Problem` is much faster than `ElementwiseProblem` for
cheap evaluations; use `ElementwiseProblem` only when each evaluation
is expensive (FEM solve, CFD run) so vectorization adds little.

## Constraints

- Inequality: `out['G'] = ...` — pymoo enforces `G <= 0`
- Equality: `out['H'] = ...` — pymoo enforces `H == 0`

Set `n_ieq_constr` / `n_eq_constr` in `super().__init__`.
