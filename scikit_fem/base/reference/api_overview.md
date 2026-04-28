# scikit-fem API Overview

> Applies to: scikit-fem 12.x

## Core imports

```python
from skfem import (
    MeshTri, MeshQuad, MeshTet, MeshHex, MeshLine,
    Basis, FacetBasis,
    ElementTriP1, ElementTriP2, ElementTetP1, ElementQuad1,
    BilinearForm, LinearForm,
    asm, condense, solve,
)
from skfem.helpers import dot, grad, div, curl, d, ddot
import numpy as np
```

## Mesh classes

| Class | Description | Built-in generators |
|-------|-------------|---------------------|
| `MeshTri` | 2D triangles | `MeshTri()` unit square, `.refined(n)` |
| `MeshQuad` | 2D quads | `MeshQuad()` |
| `MeshTet` | 3D tetrahedra | `MeshTet()` |
| `MeshHex` | 3D hexahedra | `MeshHex()` |
| `MeshLine` | 1D | `MeshLine()` |

Construction patterns:

```python
# Built-in unit square
m = MeshTri()

# Refined
m = MeshTri().refined(3)              # 4^3 = 64 subdivisions

# Load from file (needs meshio)
m = MeshTri.load("domain.msh")        # Gmsh .msh
m = MeshTri.load("domain.xdmf")

# Custom points/triangles
import numpy as np
p = np.array([[0,0],[1,0],[0,1]]).T
t = np.array([[0,1,2]]).T
m = MeshTri(p, t)
```

## Element types

Named as `Element<Geometry><Order>`:

| Element | Geometry | Polynomial order | Typical use |
|---------|----------|------------------|-------------|
| `ElementTriP1` | Triangle | linear | Poisson, diffusion |
| `ElementTriP2` | Triangle | quadratic | Higher accuracy |
| `ElementTetP1` | Tet | linear | 3D scalar |
| `ElementQuad1` | Quad | bilinear | Quad mesh scalar |
| `ElementVector(E)` | any | matches E | Vector fields (elasticity) |

## Basis

`Basis(mesh, element)` binds mesh + element = DOF numbering + integration.

```python
basis = Basis(m, ElementTriP1())
print(basis.N)                        # total DOF count
print(basis.get_dofs())               # boundary DOFs
print(basis.get_dofs("left"))         # specific facet tag
```

## Weak forms

### BilinearForm (matrix)

```python
@BilinearForm
def laplace(u, v, w):
    return dot(grad(u), grad(v))      # ∇u · ∇v
```

### LinearForm (vector)

```python
@LinearForm
def rhs(v, w):
    return 1.0 * v                    # ∫ f v dx with f=1
```

The `w` argument is a dict of globals: `w.x` (coords), `w.n` (normal),
`w["field_name"]` for externally-supplied fields.

### Assembling

```python
A = asm(laplace, basis)               # sparse matrix
b = asm(rhs, basis)                   # dense vector
```

## Solving (with Dirichlet BCs)

```python
D = basis.get_dofs()                  # all boundary DOFs
x = solve(*condense(A, b, D=D))       # u=0 on D by default
```

For non-zero Dirichlet:

```python
u0 = basis.project(lambda w: w.x[0])  # u = x on boundary
x = solve(*condense(A, b, x=u0, D=D))
```

## Common patterns

### 1) Poisson
```python
@BilinearForm
def a(u, v, w):
    return dot(grad(u), grad(v))

@LinearForm
def L(v, w):
    return 1.0 * v

A = asm(a, basis)
b = asm(L, basis)
x = solve(*condense(A, b, D=basis.get_dofs()))
```

### 2) Linear elasticity
```python
from skfem.models.elasticity import linear_elasticity, lame_parameters
E, nu = 1e9, 0.3
lam, mu = lame_parameters(E, nu)
basis = Basis(m, ElementVector(ElementTriP1()))
A = asm(linear_elasticity(lam, mu), basis)
```

### 3) Time-dependent heat
```python
# Implicit Euler: (M + dt*K) u_new = M u_old + dt*f
M = asm(mass, basis)
K = asm(laplace, basis)
dt = 0.01
for step in range(100):
    u = solve(*condense(M + dt*K, M@u_old + dt*b, D=bdry))
    u_old = u
```

## Helpers (from `skfem.helpers`)

- `dot(a, b)` — tensor inner product
- `grad(u)` — gradient
- `div(u)` — divergence (vector)
- `curl(u)` — curl (3D vector)
- `ddot(a, b)` — full contraction (two tensors)
- `d(u, i)` — partial derivative w.r.t. coord i

## Gotchas

- Form callables MUST take 3 args for `@BilinearForm` (u, v, w) or 2 for
  `@LinearForm` (v, w) — even if `w` is unused
- `condense` returns `(A_reduced, b_reduced, x_full)` — use `*condense(...)`
  to unpack into `solve()`
- `asm(form, basis)` returns scipy.sparse.csr_matrix (for bilinear) or
  numpy.ndarray (for linear)
- Performance: ~10k DOFs fine, 100k slow, 1M impractical in pure Python
