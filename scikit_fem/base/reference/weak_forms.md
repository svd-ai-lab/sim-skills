# Weak Forms in scikit-fem

> Applies to: scikit-fem 12.x

## From strong to weak form

Given a PDE in strong form:

```
-Δu = f   in Ω
u = g     on ∂Ω_D
∂u/∂n = h on ∂Ω_N
```

Multiply by test function v, integrate by parts:

```
∫_Ω ∇u · ∇v dx  =  ∫_Ω f v dx  +  ∫_∂Ω_N h v ds
       │                 │                │
       │                 │                └─ LinearForm over FacetBasis
       │                 └─ LinearForm over Basis
       └─ BilinearForm over Basis
```

Translate to scikit-fem:

```python
from skfem import BilinearForm, LinearForm
from skfem.helpers import dot, grad

@BilinearForm
def laplace(u, v, w):
    return dot(grad(u), grad(v))

@LinearForm
def rhs(v, w):
    f = 1.0  # source term (can depend on w.x for coordinates)
    return f * v
```

## Common weak forms

### Diffusion-reaction
```
∫ κ ∇u · ∇v + ∫ σ u v  =  ∫ f v
```

```python
@BilinearForm
def diffusion_reaction(u, v, w):
    kappa = 1.0
    sigma = 1.0
    return kappa * dot(grad(u), grad(v)) + sigma * u * v
```

### Advection-diffusion
```
∫ κ ∇u · ∇v + ∫ (b · ∇u) v  =  ∫ f v
```

```python
@BilinearForm
def advection_diffusion(u, v, w):
    kappa = 0.01
    b = np.array([1.0, 0.0])        # velocity field
    return kappa * dot(grad(u), grad(v)) + dot(b, grad(u)) * v
```

### Mass matrix (time-dependent problems)
```python
@BilinearForm
def mass(u, v, w):
    return u * v
```

### Linear elasticity
```python
from skfem.helpers import sym_grad, trace, ddot

@BilinearForm
def linear_elasticity(u, v, w):
    lam, mu = w["lam"], w["mu"]
    eps_u = sym_grad(u)
    eps_v = sym_grad(v)
    return lam * trace(eps_u) * trace(eps_v) + 2 * mu * ddot(eps_u, eps_v)
```

### Stokes (mixed space, block form)
```python
# Velocity-pressure block
@BilinearForm
def stokes_a(u, v, w):
    nu = 1.0
    return 2 * nu * ddot(sym_grad(u), sym_grad(v))

@BilinearForm
def stokes_b(p, v, w):
    return -p * div(v)
```

## Coordinate-dependent forms

```python
@LinearForm
def rhs(v, w):
    x, y = w.x[0], w.x[1]          # integration-point coords
    f = np.sin(np.pi * x) * np.sin(np.pi * y)
    return f * v
```

## External fields passed into forms

```python
# Pass old solution as field
@BilinearForm
def nonlinear(u, v, w):
    u_old = w["u_old"]
    return u_old * u * v

A = asm(nonlinear, basis, u_old=basis.interpolate(prev_solution))
```

## Neumann BCs (natural BCs)

Use `FacetBasis` with a specified boundary tag:

```python
from skfem import FacetBasis

fbasis = FacetBasis(mesh, element, facets=mesh.facets_satisfying(
    lambda x: x[0] == 1.0  # right edge
))

@LinearForm
def flux(v, w):
    return -2.0 * v     # specified normal flux on this boundary

b_neumann = asm(flux, fbasis)
b = asm(rhs, basis) + b_neumann
```

## Gotchas

- Return value of form functions is integrand, NOT integrated value.
  scikit-fem handles the integration via quadrature.
- `w.x` shape: `(dim, n_quad)` — per quadrature point
- `grad(u)` returns shape matching tensor rank of `u`
- For vector elements (elasticity), indexing: `u[0]`, `u[1]`, ...
