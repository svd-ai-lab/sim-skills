# pymoo workflow

```python
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.problems import get_problem
from pymoo.optimize import minimize

# Built-in benchmark
problem  = get_problem('zdt1')                  # 30-var, 2-obj
algo     = NSGA2(pop_size=40)
res      = minimize(problem, algo, ('n_gen', 50), seed=1, verbose=False)

# Multi-obj results
print(res.F.shape)         # (k, n_obj)  Pareto front
print(res.X.shape)         # (k, n_var)  design vectors
```

## User-defined problem (ElementwiseProblem)

```python
import numpy as np
from pymoo.core.problem import ElementwiseProblem

class MyProblem(ElementwiseProblem):
    def __init__(self):
        super().__init__(
            n_var=2, n_obj=2, n_ieq_constr=1,
            xl=np.array([-2, -2]), xu=np.array([2, 2]),
        )
    def _evaluate(self, x, out, *args, **kwargs):
        out['F'] = [x[0]**2 + x[1]**2,  (x[0]-1)**2 + x[1]**2]
        out['G'] = [x[0] + x[1] - 1.0]      # G <= 0 enforced

problem = MyProblem()
res = minimize(problem, NSGA2(pop_size=40), ('n_gen', 50), seed=1)
```

## Single-objective

```python
from pymoo.algorithms.soo.nonconvex.de import DE
res = minimize(get_problem('rastrigin'), DE(pop_size=50), ('n_gen', 100), seed=1)
print(res.F[0])      # best objective value
print(res.X[0])      # best design
```

## Always emit JSON

```python
import json
print(json.dumps({
    "ok": True,
    "n_pareto": int(len(res.F)),
    "f_best": [float(x) for x in res.F[0]],
}))
```
