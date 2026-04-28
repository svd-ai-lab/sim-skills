# CoolProp PropsSI workflow

## Single property query

```python
from CoolProp.CoolProp import PropsSI

# Signature: PropsSI(target, in1_name, in1_val, in2_name, in2_val, fluid)
# Inputs and outputs are ALL SI: Pa, K, J/kg, kg/m^3, Pa*s, W/m/K

# Steam at 300 K, 1 atm
h = PropsSI('H', 'T', 300.0, 'P', 101325, 'Water')         # J/kg
s = PropsSI('S', 'T', 300.0, 'P', 101325, 'Water')         # J/kg/K
rho = PropsSI('D', 'T', 300.0, 'P', 101325, 'Water')       # kg/m^3

# Saturation at 1 atm: vapor quality Q
T_sat = PropsSI('T', 'P', 101325, 'Q', 0, 'Water')          # K
h_l   = PropsSI('H', 'P', 101325, 'Q', 0, 'Water')          # liquid
h_v   = PropsSI('H', 'P', 101325, 'Q', 1, 'Water')          # vapor
h_fg  = h_v - h_l                                            # latent

# Refrigerant
mu = PropsSI('V', 'T', 250.0, 'P', 5e5, 'R134a')             # viscosity
```

## Vectorized queries (numpy arrays)

```python
import numpy as np
T = np.linspace(280, 380, 11)
rho = PropsSI('D', 'T', T, 'P', 101325, 'Water')             # array out
```

## Humid-air psychrometrics

Different function: `HAPropsSI`. Inputs include relative humidity (`R`)
or humidity ratio (`W`).

```python
from CoolProp.HumidAirProp import HAPropsSI
h = HAPropsSI('H', 'T', 300.0, 'P', 101325, 'R', 0.5)   # 50 % RH
```

## Always emit JSON

```python
import json
print(json.dumps({
    "ok": True,
    "T_sat_K": float(T_sat),
    "h_fg_J_per_kg": float(h_fg),
}))
```
