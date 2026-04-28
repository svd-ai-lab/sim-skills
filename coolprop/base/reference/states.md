# State input pairs

Single-phase: pick any two independent properties.
Saturation: use Q (vapor quality) with one of T or P.

## Common pairs

| Pair | Use for |
|---|---|
| `(T, P)` | single-phase points (most common) |
| `(P, Q)` | saturation curve at given P |
| `(T, Q)` | saturation curve at given T |
| `(H, P)` | isenthalpic (e.g., throttling out state) |
| `(S, P)` | isentropic (e.g., turbine/compressor ideal) |
| `(D, T)` | when density is the natural state var |
| `(U, V)` | constant volume + internal energy |

## Two-phase: Q ∈ [0, 1]

```python
PropsSI('H', 'P', 1e5, 'Q', 0,    'Water')   # saturated liquid
PropsSI('H', 'P', 1e5, 'Q', 1,    'Water')   # saturated vapor
PropsSI('H', 'P', 1e5, 'Q', 0.5,  'Water')   # 50/50 mixture
```

## Throttling example (refrigeration cycle)

```python
# Inlet state: T=40C, saturated liquid R134a
P_inlet  = PropsSI('P', 'T', 313.15, 'Q', 0, 'R134a')
h_inlet  = PropsSI('H', 'T', 313.15, 'Q', 0, 'R134a')

# Outlet: same enthalpy, lower pressure
P_outlet = 2e5
T_outlet = PropsSI('T', 'P', P_outlet, 'H', h_inlet, 'R134a')
Q_outlet = PropsSI('Q', 'P', P_outlet, 'H', h_inlet, 'R134a')
```
