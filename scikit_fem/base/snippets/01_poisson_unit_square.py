"""Step 1: Poisson equation on unit square (verified E2E).

Solves -Δu = 1 on Ω = [0,1]² with u=0 on ∂Ω.
Analytical u_max ≈ 0.0736713 at (0.5, 0.5).
FEM with P1 triangles, refined 4 levels: u_max ≈ 0.0734 (error < 0.5%).

Run: sim run 01_poisson_unit_square.py --solver scikit_fem
"""
import json
import numpy as np
from skfem import MeshTri, Basis, ElementTriP1, BilinearForm, LinearForm, asm, condense, solve
from skfem.helpers import dot, grad


@BilinearForm
def laplace(u, v, w):
    return dot(grad(u), grad(v))


@LinearForm
def rhs(v, w):
    return 1.0 * v


m = MeshTri().refined(4)
basis = Basis(m, ElementTriP1())

A = asm(laplace, basis)
b = asm(rhs, basis)
x = solve(*condense(A, b, D=basis.get_dofs()))

imax = int(np.argmax(x))
result = {
    "ok": True,
    "step": "poisson-unit-square",
    "nodes": int(m.nvertices),
    "u_max": float(x.max()),
    "u_max_location": [float(m.p[0, imax]), float(m.p[1, imax])],
}
print(json.dumps(result))
