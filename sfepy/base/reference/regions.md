# Region selectors

Created via `domain.create_region(name, selector, kind)`.

## Selectors

```python
'all'                                          # whole mesh
'vertices in (x < 0.001)'                      # left edge
'vertices in (x > 0.999)'                      # right edge
'vertices in (y < 0.001) | (y > 0.999)'        # top + bottom
'vertices by some_function'                    # via callable
'cells of group 1'                             # by mesh group
'r.A *v r.B'                                   # set ops between regions
```

## Kinds

| Kind | Use for | Required by terms |
|---|---|---|
| `'cell'` (default) | volume integration | `dw_laplace`, `dw_lin_elastic`, ... |
| `'facet'` | surface / Neumann / Dirichlet | `dw_surface_ltr`, `EssentialBC` |
| `'edge'` | 3D edge integration | rare |
| `'vertex'` | point loads / nodal BCs | special use |

## Common patterns

```python
omega   = domain.create_region('Omega', 'all')
left    = domain.create_region('Left',  'vertices in (x < 0.001)', 'facet')
right   = domain.create_region('Right', 'vertices in (x > 0.999)', 'facet')
bottom  = domain.create_region('Bot',   'vertices in (y < 0.001)', 'facet')
gamma_d = domain.create_region(
    'Dirichlet',
    'vertices in (x < 0.001) | (x > 0.999) | (y < 0.001) | (y > 0.999)',
    'facet',
)
```

## Tolerances

Use small tolerances (`< 0.001`) instead of strict equality (`x == 0`) —
mesh vertex coordinates have float-precision noise.
