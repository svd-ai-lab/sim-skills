"""Step 1: Poisson -Δu = 1 on unit square (verified E2E).

Acceptance: u_max within 5% of analytical 0.073671.
Observed:   0.07460 (~1.3% error) on 8x8 quad mesh.

Run: sim run 01_poisson.py --solver sfepy
"""
import json
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


def main():
    mesh = gen_block_mesh([1.0, 1.0], [9, 9], [0.5, 0.5], name='block')
    domain = FEDomain('domain', mesh)
    omega = domain.create_region('Omega', 'all')
    gamma = domain.create_region(
        'Gamma',
        'vertices in (x < 0.001) | (x > 0.999) | (y < 0.001) | (y > 0.999)',
        'facet',
    )

    field = Field.from_args('fu', np.float64, 'scalar', omega, approx_order=1)
    u = FieldVariable('u', 'unknown', field)
    v = FieldVariable('v', 'test', field, primary_var_name='u')

    m = Material('m', val=1.0)
    f = Material('f', val=1.0)
    integral = Integral('i', order=2)

    t1 = Term.new('dw_laplace(m.val, v, u)', integral, omega, m=m, v=v, u=u)
    t2 = Term.new('dw_volume_lvf(f.val, v)', integral, omega, f=f, v=v)
    eq = Equation('Poisson', t1 - t2)
    eqs = Equations([eq])

    pb = Problem('Poisson', equations=eqs)
    pb.set_bcs(ebcs=Conditions([EssentialBC('fix', gamma, {'u.0': 0.0})]))
    pb.set_solver(Newton({}, lin_solver=ScipyDirect({})))
    state = pb.solve()
    sol = state.get_state_parts()['u']

    u_max = float(sol.max())
    rel = abs(u_max - 0.073671) / 0.073671
    print(json.dumps({"ok": rel < 0.05, "u_max": u_max, "rel_error": rel}))


if __name__ == "__main__":
    main()
