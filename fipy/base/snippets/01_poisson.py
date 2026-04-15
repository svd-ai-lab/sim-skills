"""Step 1: 1D steady Poisson on [0,1] with phi(0)=1, phi(1)=0 (verified E2E).

Analytical: phi(x) = 1 - x. Mid (x=0.49) -> 0.49.
Observed: 0.49 (error 1.6e-15) on 50 cells.

Run: sim run 01_poisson.py --solver fipy
"""
import json
from fipy import CellVariable, Grid1D, DiffusionTerm


def main():
    nx, dx = 50, 1.0 / 50
    mesh = Grid1D(nx=nx, dx=dx)
    phi = CellVariable(name='phi', mesh=mesh, value=0.5)
    phi.constrain(1.0, mesh.facesLeft)
    phi.constrain(0.0, mesh.facesRight)

    eq = DiffusionTerm(coeff=1.0) == 0
    eq.solve(var=phi)

    mid = float(phi.value[nx // 2])
    expected = 1.0 - (nx // 2 + 0.5) * dx
    print(json.dumps({
        "ok": abs(mid - expected) < 0.01,
        "mid_value": mid,
        "expected": expected,
        "abs_error": abs(mid - expected),
    }))


if __name__ == "__main__":
    main()
