# Common SfePy weak-form terms

Compose with `Term.new('term_name(args)', integral, region, **named)`.

## Scalar PDEs

| Term | Weak form | Use for |
|---|---|---|
| `dw_laplace(m.val, v, u)` | ∫ m ∇v·∇u | Poisson, heat, Laplace |
| `dw_volume_dot(c.val, v, u)` | ∫ c v u | mass / reaction |
| `dw_volume_lvf(f.val, v)` | ∫ f v | source / forcing |
| `dw_surface_ltr(t.val, v)` | ∫_Γ t·v | Neumann / traction |

## Vector / elasticity

| Term | Weak form | Use for |
|---|---|---|
| `dw_lin_elastic(D.D, v, u)` | ∫ D : ε(v) : ε(u) | linear elasticity |
| `dw_lin_elastic_iso(m.lam, m.mu, v, u)` | isotropic Lamé form | simpler isotropic |
| `dw_volume_lvf(f.val, v)` | body force | gravity / load |
| `dw_surface_ltr(t.val, v)` | surface traction | applied stress |

## Convection / Navier-Stokes

| Term | Weak form | Use for |
|---|---|---|
| `dw_div(v, p)` | ∫ ∇·v p | divergence (NS) |
| `dw_grad(v, p)` | ∫ v ∇p | gradient (NS) |
| `dw_convect(v, u)` | ∫ (u·∇) u · v | convection |

## Time-dependent

| Term | Weak form | Use for |
|---|---|---|
| `dw_dot(c.val, v, u)` | identical to `volume_dot` | M (mass matrix) |
| `dw_div_grad(c.val, v, u)` | for diffusion-like terms in transients |  |

## How to discover more

```python
from sfepy.terms import term_table
print(sorted(term_table.keys()))
```

The full registry is large (100+ terms). The categories above cover
~80% of typical use.
