# Solvers

## AC power flow — `runpp`

```python
pp.runpp(
    net,
    algorithm='nr',        # 'nr' (Newton-Raphson, default), 'iwamoto_nr',
                            # 'fdbx' (fast decoupled), 'fdxb', 'gs' (Gauss-Seidel),
                            # 'dc' (DC PF — linear approx)
    init='auto',           # 'flat', 'dc', 'results', 'auto'
    max_iteration='auto',
    tolerance_mva=1e-8,
    enforce_q_lims=False,
    numba=True,            # speed; set False if numba not installed
)
```

Convergence is reflected by `net.converged` (True/False after the call).

## Optimal power flow — `runopp`

```python
pp.runopp(
    net,
    delta=1e-10,
    init='flat',
    calculate_voltage_angles=True,
    suppress_warnings=False,
    switch_rx_ratio=2,
)
# Result table includes economic dispatch:
print(net.res_cost)
```

Requires PYPOWER or PowerModels.jl backend (PYPOWER bundled with pandapower).

## Short-circuit — `runsc`

```python
import pandapower.shortcircuit as sc
sc.calc_sc(net, fault='3ph', case='max', ip=True, ith=True)
print(net.res_bus_sc)
```

## Time-series — `run_timeseries`

```python
from pandapower.timeseries import OutputWriter, DFData, ConstControl
from pandapower.control import ConstControl

# Build profiles, define controllers, OutputWriter
# Then:
from pandapower.timeseries import run_timeseries
run_timeseries(net, time_steps=range(96))    # e.g., 15-min intervals over a day
```

## Three-phase PF — `runpp_3ph`

```python
pp.runpp_3ph(net)        # for unbalanced LV networks
print(net.res_bus_3ph)   # vm_a/b/c, va_a/b/c
```
