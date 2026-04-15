# Reactor / ReactorNet usage

| Class | Conserved | Use for |
|---|---|---|
| `IdealGasReactor` | mass, energy, species | constant-volume batch (closed) |
| `IdealGasConstPressureReactor` | mass, enthalpy, species | constant-pressure batch |
| `Reactor` (real-gas) | same as IdealGas, real EoS | non-ideal gas |
| `FlowReactor` | mass, energy + length param | PFR (1D plug flow) |
| `Reservoir` | none (held fixed) | upstream/downstream BC |

## Connecting reactors

```python
res_in   = ct.Reservoir(gas_inlet)
res_out  = ct.Reservoir(gas_dump)
reactor  = ct.IdealGasReactor(gas)
mfc      = ct.MassFlowController(res_in, reactor, mdot=1e-4)
valve    = ct.PressureController(reactor, res_out, primary=mfc, K=1e-6)
net      = ct.ReactorNet([reactor])
```

## Time integration

```python
net = ct.ReactorNet([r])
net.atol = 1e-12
net.rtol = 1e-7
t = 0.0
while t < t_end:
    t = net.step()                # adaptive
# or fixed steps:
times = np.linspace(0, t_end, n)
for t in times: net.advance(t)
```

## Tips

- `Reactor.thermo` and `Reactor.kinetics` access the underlying gas state.
- For ignition delay: track when `T` rises above (T_init + 400 K) — that's
  the standard convention.
- For CHEMKIN-style sensitivity, use `r.add_sensitivity_reaction(idx)` then
  `net.sensitivity('T', t, k)` after solving.
