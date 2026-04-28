# SfePy direct-API workflow

```python
import numpy as np
from sfepy.discrete.fem import FEDomain, Field
from sfepy.discrete import (
    FieldVariable, Material, Integral, Equation, Equations, Problem,
)
from sfepy.terms import Term
from sfepy.discrete.conditions import Conditions, EssentialBC
from sfepy.solvers.ls import ScipyDirect
from sfepy.solvers.nls import Newton
from sfepy.mesh.mesh_generators import gen_block_mesh

# 1. Mesh
mesh = gen_block_mesh([Lx, Ly], [nx, ny], [cx, cy], name='block')

# 2. Domain + regions
domain = FEDomain('domain', mesh)
omega  = domain.create_region('Omega', 'all')
gamma  = domain.create_region(
    'Gamma',
    'vertices in (x < 0.001) | (x > 0.999)',
    'facet',
)

# 3. Field + variables
field = Field.from_args('fu', np.float64, 'scalar', omega, approx_order=1)
u = FieldVariable('u', 'unknown', field)
v = FieldVariable('v', 'test', field, primary_var_name='u')

# 4. Materials & integrals
m = Material('m', val=1.0)
f = Material('f', val=1.0)
integral = Integral('i', order=2)

# 5. Terms (weak form pieces)
t1 = Term.new('dw_laplace(m.val, v, u)', integral, omega, m=m, v=v, u=u)
t2 = Term.new('dw_volume_lvf(f.val, v)', integral, omega, f=f, v=v)

# 6. Equation + equations
eq = Equation('Poisson', t1 - t2)
eqs = Equations([eq])

# 7. Boundary conditions
bc = EssentialBC('fix', gamma, {'u.0': 0.0})

# 8. Problem + solvers
pb = Problem('Poisson', equations=eqs)
pb.set_bcs(ebcs=Conditions([bc]))
pb.set_solver(Newton({}, lin_solver=ScipyDirect({})))

# 9. Solve and read out
state = pb.solve()
sol = state.get_state_parts()['u']        # NumPy array of DOF values
print({"u_max": float(sol.max())})
```

For nonlinear / time-dependent problems, replace step 8/9 with
the appropriate solver (`Newton` already handles nonlinear; for
transients use `pb.create_solver(...)` with an evolutionary nls).
