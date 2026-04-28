# Boundary Conditions in scikit-fem

> Applies to: scikit-fem 12.x

## Dirichlet BCs via `condense`

```python
D = basis.get_dofs()                     # all boundary DOFs
x = solve(*condense(A, b, D=D))          # homogeneous u=0 on D
```

### Non-homogeneous Dirichlet

```python
u_bc = basis.project(lambda w: w.x[0])   # u = x on boundary
x = solve(*condense(A, b, x=u_bc, D=D))
```

### Targeting specific boundaries

```python
# By predicate
left = basis.get_dofs(lambda x: x[0] == 0.0)

# By facet tag (if mesh has labels)
inlet = basis.get_dofs("inlet")

x = solve(*condense(A, b, D=left))
```

### Combining multiple BC regions

```python
left  = basis.get_dofs(lambda x: x[0] == 0.0)
right = basis.get_dofs(lambda x: x[0] == 1.0)
D = np.concatenate([left, right])

# Different values on each
u_bc = np.zeros(basis.N)
u_bc[left] = 0.0
u_bc[right] = 1.0

x = solve(*condense(A, b, x=u_bc, D=D))
```

## Neumann BCs (natural)

Incorporate via boundary integral on RHS using `FacetBasis`:

```python
from skfem import FacetBasis

# Boundary subset
fbasis = FacetBasis(mesh, element, facets=mesh.facets_satisfying(
    lambda x: x[0] == 1.0
))

@LinearForm
def flux(v, w):
    return 5.0 * v                        # ∫ 5 v ds on right edge

b_neumann = asm(flux, fbasis)
b_total = asm(rhs, basis) + b_neumann
```

Homogeneous Neumann ("do nothing" / natural) requires no code — just
don't constrain those DOFs.

## Robin BCs (mixed)

```
α u + β ∂u/∂n = γ  on Γ_R
```

Contributes to both LHS (α u v) and RHS (γ v / β):

```python
@BilinearForm
def robin_lhs(u, v, w):
    alpha, beta = 1.0, 1.0
    return (alpha / beta) * u * v

@LinearForm
def robin_rhs(v, w):
    beta, gamma = 1.0, 2.0
    return (gamma / beta) * v

A_robin = asm(robin_lhs, fbasis)
b_robin = asm(robin_rhs, fbasis)
A_total = A + A_robin
b_total = b + b_robin
```

## Periodic BCs

Use `MappedBasis` to tie DOFs on opposing boundaries:

```python
from skfem import MappingAffine
# See skfem.assembly.Basis.with_element and MappedBasis docs
# Typical pattern: identify pairs, eliminate redundant DOFs
```

This is more advanced; see scikit-fem docs for full pattern.

## Gotchas

- `basis.get_dofs()` without args returns ALL boundary DOFs
- `get_dofs(predicate)` filters by geometric condition on boundary
- `condense(A, b, x=x0, D=D)` — x0 is used to supply non-zero Dirichlet
  values; final solution is `x` where `x[D] = x0[D]`
- For vector-valued elements, DOF numbering interleaves components:
  `basis.get_dofs(...)` returns DOFs for ALL components unless filtered
- Facet tags require mesh to have been loaded with labels (from .msh)
  or defined via `mesh.with_boundaries({"tag": predicate})`
