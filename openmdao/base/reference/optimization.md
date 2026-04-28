# Optimization workflow

```python
prob.driver = om.ScipyOptimizeDriver(
    optimizer='SLSQP',          # or 'COBYLA', 'L-BFGS-B', 'differential_evolution'
    tol=1e-8,
    disp=True,
)

# Design variables (with bounds)
model.add_design_var('x',  lower=-5, upper=5)
model.add_design_var('z',  lower=np.array([-10, 0]), upper=np.array([10, 10]))

# Objective (single)
model.add_objective('f_obj')

# Constraints (inequality / equality)
model.add_constraint('g1', upper=0.0)        # g1 <= 0
model.add_constraint('g2', equals=0.0)       # g2 == 0
model.add_constraint('g3', lower=1.0, upper=5.0)
```

## Other drivers

| Driver | Use for |
|---|---|
| `ScipyOptimizeDriver` | gradient-based + a few gradient-free (SciPy-backed) |
| `pyOptSparseDriver` | SNOPT, IPOPT, NLPQL (requires `pyoptsparse`) |
| `DOEDriver` | parametric sweeps (LHS, FullFactorial, Uniform) |
| `GeneticAlgorithmDriver` | OpenMDAO built-in GA |

## DOE example

```python
prob.driver = om.DOEDriver(om.LatinHypercubeGenerator(samples=20))
prob.driver.add_recorder(om.SqliteRecorder('cases.sql'))
prob.run_driver()

cr = om.CaseReader('cases.sql')
cases = cr.list_cases()
for c in cases:
    case = cr.get_case(c)
    print(case['x'], case['f_obj'])
```

## Optimization acceptance

For acceptance, check:
- `prob.driver.iter_count > 0` (driver actually iterated)
- `f_obj` improved from initial value
- All constraint values within tolerance
- Final design vars within bounds
