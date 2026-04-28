# Backend solvers

Pyomo dispatches the model to one of these. **Each must be installed
separately**; `pip install pyomo` brings the framework, NOT the solver.

## Open-source

| Backend | Problem class | How to install |
|---|---|---|
| `appsi_highs` | LP, MIP | `pip install highspy` (pure pip!) |
| `glpk` | LP, MIP | system: `apt install glpk-utils` |
| `cbc` | LP, MIP | system: `apt install coinor-cbc` |
| `ipopt` | NLP | system: `apt install coinor-ipopt`, or via conda |
| `bonmin` | MINLP | conda: `conda install -c conda-forge coincbc bonmin` |
| `couenne` | global MINLP | conda: `conda install -c conda-forge couenne` |

## Commercial

| Backend | Problem class | License |
|---|---|---|
| `gurobi` | LP/MIP/QP/MIQP/MIQCP | commercial; free academic |
| `cplex` | LP/MIP/QP | commercial; free community |
| `xpress` | LP/MIP/QP | commercial |
| `mosek` | LP/SOCP/SDP | commercial; free academic |

## Solver discovery pattern

```python
solver = None
for name in ('appsi_highs', 'glpk', 'cbc', 'ipopt'):
    try:
        s = pyo.SolverFactory(name)
        if s.available(exception_flag=False):
            solver = s; break
    except Exception:
        pass
if solver is None:
    raise RuntimeError("no Pyomo backend solver found")
```

## Solver options (per-backend)

```python
solver = pyo.SolverFactory('appsi_highs')
solver.config.time_limit = 30           # seconds
solver.config.mip_gap   = 0.01

solver = pyo.SolverFactory('ipopt')
solver.options['max_iter'] = 200
solver.options['tol']      = 1e-8
```
