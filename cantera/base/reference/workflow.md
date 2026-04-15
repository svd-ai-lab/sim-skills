# Cantera workflow patterns

## Pattern 1: Equilibrium

```python
import cantera as ct
g = ct.Solution('gri30.yaml')
g.TPX = 300, ct.one_atm, 'CH4:1, O2:2, N2:7.52'   # state
g.equilibrate('HP')                                # constant H, P
print(g.T, g.X)                                    # adiabatic T, eq composition
```

## Pattern 2: Well-stirred reactor (perfectly stirred volume)

```python
g = ct.Solution('gri30.yaml')
g.TPX = 1500, ct.one_atm, 'CH4:1, O2:2, N2:7.52'
r = ct.IdealGasReactor(g)
net = ct.ReactorNet([r])
times, T = [], []
t = 0.0
while t < 0.01:
    t = net.step()
    times.append(t); T.append(r.T)
```

## Pattern 3: Premixed flame (1D)

```python
g = ct.Solution('gri30.yaml')
g.TPX = 300, ct.one_atm, 'CH4:1, O2:2, N2:7.52'
f = ct.FreeFlame(g, width=0.03)
f.set_refine_criteria(ratio=3, slope=0.06, curve=0.12)
f.solve(loglevel=0, auto=True)
print('flame speed [cm/s]:', f.velocity[0] * 100)
```

## Pattern 4: Counterflow diffusion flame

```python
oxidizer = ct.Solution('gri30.yaml'); oxidizer.TPX = 300, p, 'O2:0.21, N2:0.79'
fuel     = ct.Solution('gri30.yaml'); fuel.TPX     = 300, p, 'CH4:1'
f = ct.CounterflowDiffusionFlame(oxidizer, fuel, width=0.02)
f.fuel_inlet.mdot = 0.24
f.oxidizer_inlet.mdot = 0.72
f.solve(loglevel=0)
```

## Pattern 5: Plug-flow reactor (PFR via marching ODE)

```python
g = ct.Solution('gri30.yaml')
g.TPX = 1500, ct.one_atm, 'CH4:1, O2:2, N2:7.52'
r = ct.IdealGasConstPressureReactor(g)
net = ct.ReactorNet([r])
# advance distance via mass-balance: dz = u * dt
```

## Always emit JSON

```python
import json
print(json.dumps({
    "ok": True,
    "T_K": float(g.T),
    "X_CO2": float(g['CO2'].X[0]),
}))
```
