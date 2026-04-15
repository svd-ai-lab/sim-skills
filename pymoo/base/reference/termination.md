# Termination criteria

Passed as the third positional arg to `minimize`.

## Tuple shorthand

```python
('n_gen', 50)             # 50 generations
('n_eval', 5000)          # 5000 evaluations
('time', '00:01:00')      # 1 minute wall clock
```

## Class-based (full API)

```python
from pymoo.termination import get_termination

term = get_termination('n_gen', 50)
term = get_termination('time', '00:00:30')
res  = minimize(problem, algo, term, seed=1)
```

## Multi-criteria default (DefaultMultiObjectiveTermination)

Stops when ANY of: max gens reached, hypervolume converged, design var
movement below tolerance.

```python
from pymoo.termination.default import DefaultMultiObjectiveTermination
term = DefaultMultiObjectiveTermination(
    xtol=1e-6, cvtol=1e-6, ftol=1e-6, period=20, n_max_gen=200,
)
```
