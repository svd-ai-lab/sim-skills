# Solvers

## Nonlinear (residual loop)

| Solver | Use when |
|---|---|
| `NonlinearBlockGS` | weakly coupled, fast, no jacobian needed |
| `NonlinearRunOnce` | explicit (DAG) — no cycles |
| `NewtonSolver` | strongly coupled, needs accurate jacobian (analytic or CS/FD) |
| `BroydenSolver` | quasi-Newton, no jacobian rebuild each iter |

## Linear (derivative computation)

| Solver | Use when |
|---|---|
| `DirectSolver` | small (< few k DOFs), accurate |
| `LinearBlockGS` | weakly coupled |
| `ScipyKrylov` | iterative, large problems |
| `PETScKrylov` | parallel iterative (requires petsc4py) |

## Pattern for coupled groups

```python
group.nonlinear_solver = om.NewtonSolver(solve_subsystems=False)
group.nonlinear_solver.options['maxiter'] = 50
group.nonlinear_solver.options['atol']    = 1e-10
group.linear_solver    = om.DirectSolver()
```

## Pattern for derivative checking

```python
prob.check_partials(compact_print=True)        # analytic vs finite-diff
prob.check_totals()                             # end-to-end derivatives
```
