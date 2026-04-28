# Algorithms

## Multi-objective (MOO)

| Algorithm | Use when |
|---|---|
| `NSGA2` (`pymoo.algorithms.moo.nsga2`) | 2-3 objectives, default workhorse |
| `NSGA3` (`pymoo.algorithms.moo.nsga3`) | many-obj (4+); needs reference directions |
| `MOEAD` (`pymoo.algorithms.moo.moead`) | scalarization-based, large pop |
| `RNSGA2` | reference-point guided 2-obj |
| `RNSGA3` | reference-point guided many-obj |
| `UNSGA3` | unified NSGA-III (1+ obj) |
| `CTAEA` | constrained two-archive |

## Single-objective (SOO)

| Algorithm | Module | Use when |
|---|---|---|
| `GA` | `pymoo.algorithms.soo.nonconvex.ga` | generic real-valued |
| `DE` | `pymoo.algorithms.soo.nonconvex.de` | continuous, robust |
| `PSO` | `pymoo.algorithms.soo.nonconvex.pso` | well-known baseline |
| `CMAES` | `pymoo.algorithms.soo.nonconvex.cmaes` | small-dim, smooth |
| `BRKGA` | `pymoo.algorithms.soo.nonconvex.brkga` | combinatorial / permutation |

## NSGA-III pattern (needs reference directions)

```python
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.util.ref_dirs import get_reference_directions

ref_dirs = get_reference_directions("uniform", n_dim=3, n_partitions=12)
algo     = NSGA3(pop_size=92, ref_dirs=ref_dirs)
res      = minimize(get_problem('dtlz1', n_var=7, n_obj=3), algo, ('n_gen', 400))
```

## Common knobs

```python
NSGA2(
    pop_size=100,
    sampling=...,             # initial population sampler
    crossover=SBX(prob=0.9),
    mutation=PM(eta=20),
    eliminate_duplicates=True,
)
```
