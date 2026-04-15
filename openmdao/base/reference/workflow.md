# OpenMDAO standard workflow

```python
import openmdao.api as om

# 1. Problem & top-level model
prob = om.Problem()
model = prob.model

# 2. Add components / groups (with promotes for shared variables)
model.add_subsystem('a', MyComp1(), promotes=['*'])
model.add_subsystem('b', MyComp2(), promotes=['*'])

# 3. (For coupled groups) attach a nonlinear solver
model.nonlinear_solver = om.NonlinearBlockGS()    # or NewtonSolver
model.linear_solver    = om.DirectSolver()        # for derivatives

# 4. (For optimization) attach a driver and declare design vars / obj / cons
prob.driver = om.ScipyOptimizeDriver(optimizer='SLSQP', tol=1e-8)
model.add_design_var('x', lower=-10, upper=10)
model.add_objective('f_obj')
model.add_constraint('g1', upper=0.0)

# 5. Initial values (for promoted inputs)
model.set_input_defaults('x', 1.0)
model.set_input_defaults('z', np.array([5.0, 2.0]))

# 6. Set up data graph (mandatory before run)
prob.setup()

# 7. Run (analysis only OR optimization)
prob.run_model()        # MDA only
prob.run_driver()       # full optimization

# 8. Read results
print(prob['x'], prob['f_obj'])
```

## Always emit JSON

```python
import json
print(json.dumps({
    "ok": True,
    "x": float(prob['x']),
    "f_obj": float(prob['f_obj']),
}))
```
