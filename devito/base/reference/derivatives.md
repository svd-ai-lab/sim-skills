# Symbolic derivatives

Devito attaches `.dx`, `.dt`, etc. to `Function` / `TimeFunction`.
Order is determined by `space_order=` / `time_order=` on the function.

## First-order

| Notation | Meaning |
|---|---|
| `u.dx`, `u.dy`, `u.dz` | ∂u/∂x, ∂u/∂y, ∂u/∂z |
| `u.dt` | ∂u/∂t (forward by default) |
| `u.dxc` | centered ∂u/∂x (when relevant) |

## Second-order

| Notation | Meaning |
|---|---|
| `u.dx2` | ∂²u/∂x² |
| `u.dy2` | ∂²u/∂y² |
| `u.dz2` | ∂²u/∂z² |
| `u.dt2` | ∂²u/∂t² |
| `u.laplace` | ∇²u (sum of dx2 + dy2 + dz2) |

## Mixed

```python
u.dxdy        # ∂²u/∂x∂y
u.dxdz, u.dydz, u.dxdt, ...
```

## Time

```python
u.forward    # u^{n+1}  (next time step)
u.backward   # u^{n-1}
u            # u^n
```

## Build PDEs by combining

```python
# 2D acoustic wave with point source f
pde = m * u.dt2 - (u.dx2 + u.dy2) - f         # f is a SparseTimeFunction

# Heat with anisotropic diffusivity
pde = u.dt - (kx * u.dx2 + ky * u.dy2)
```

The compiler chooses stencil weights based on the function's
`space_order` (e.g., 2, 4, 8 for 2nd / 4th / 8th-order accurate).
