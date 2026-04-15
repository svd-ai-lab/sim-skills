# 1D flame solvers

## FreeFlame — laminar premixed flame, free propagation

```python
g = ct.Solution('gri30.yaml')
g.TPX = 300, ct.one_atm, 'CH4:1, O2:2, N2:7.52'
f = ct.FreeFlame(g, width=0.03)
f.set_refine_criteria(ratio=3, slope=0.06, curve=0.12)
f.solve(loglevel=0, auto=True)
S_L = f.velocity[0]                        # m/s
```

Typical CH4/air S_L at φ=1: ~38 cm/s.

## BurnerFlame — premixed stabilized on a burner

```python
f = ct.BurnerFlame(g, width=0.02)
f.burner.mdot = 0.06                        # kg/m^2 s
f.solve(loglevel=0)
```

## CounterflowDiffusionFlame — non-premixed counterflow

```python
ox  = ct.Solution('gri30.yaml'); ox.TPX  = 300, p, 'O2:0.21, N2:0.79'
fu  = ct.Solution('gri30.yaml'); fu.TPX  = 300, p, 'CH4:1'
f = ct.CounterflowDiffusionFlame(ox, fu, width=0.02)
f.fuel_inlet.mdot     = 0.24
f.oxidizer_inlet.mdot = 0.72
f.solve(loglevel=0)
```

## Refinement criteria

| Param | Meaning | Tighter | Looser |
|---|---|---|---|
| `ratio` | max ratio of adjacent grid spacings | 2 | 5 |
| `slope` | max relative change in any solution variable | 0.02 | 0.1 |
| `curve` | max relative change in slope | 0.02 | 0.2 |

Tighter = more grid points, slower, more accurate. Start with
`ratio=3, slope=0.06, curve=0.12` and tighten if results are not
grid-converged.

## Transport models

```python
g = ct.Solution('gri30.yaml')
g.transport_model = 'Mix'           # default — mixture-averaged
g.transport_model = 'Multi'         # multicomponent (slower, more accurate)
```
