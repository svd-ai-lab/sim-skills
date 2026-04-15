# Setting thermodynamic state

Cantera state setters take **tuples**, not method calls. Always set
all variables at once.

| Setter | Tuple | Notes |
|---|---|---|
| `TPX` | (T, P, X) | T [K], P [Pa], X = mole fraction string or array |
| `TPY` | (T, P, Y) | Y = mass fraction |
| `TP` | (T, P) | composition unchanged |
| `HP` | (h, P) | enthalpy [J/kg], pressure [Pa] |
| `SP` | (s, P) | entropy, pressure (isentropic) |
| `UV` | (u, v) | internal energy, specific volume |
| `DPX` | (rho, P, X) | density, pressure, composition |

## Composition string syntax

```
'CH4:1, O2:2, N2:7.52'      # space-separated species:moles, normalized internally
'H2:0.10, O2:0.05, N2:0.85' # may be mole or mass fractions per setter
```

## Equivalence ratio helper

```python
g.set_equivalence_ratio(phi=1.0, fuel='CH4', oxidizer='O2:1, N2:3.76')
```
Sets composition stoichiometrically without manual ratio computation.

## Common defaults

```python
ct.one_atm                       # 101325 Pa
g.P_atm = g.P / ct.one_atm       # convenient unit conversion
```
