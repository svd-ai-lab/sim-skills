# Property codes

CoolProp uses single-letter codes for the most common properties.
Full table (extract):

| Code | Property | SI units |
|---|---|---|
| `T` | Temperature | K |
| `P` | Pressure | Pa |
| `D` | Density | kg/m³ |
| `H` | Enthalpy | J/kg |
| `S` | Entropy | J/kg/K |
| `U` | Internal energy | J/kg |
| `Q` | Vapor quality | dimensionless [0..1] |
| `C` | Cp (isobaric specific heat) | J/kg/K |
| `O` | Cv (isochoric specific heat) | J/kg/K |
| `A` | Speed of sound | m/s |
| `V` | Viscosity | Pa·s |
| `L` | Thermal conductivity | W/m/K |
| `M` | Molar mass | kg/mol |
| `Z` | Compressibility factor | dimensionless |
| `Tcrit` | Critical T | K |
| `Pcrit` | Critical P | Pa |
| `Ttriple` | Triple-point T | K |
| `Tmin` | EoS lower T limit | K |
| `Tmax` | EoS upper T limit | K |

## Critical / triple / EoS limits (constants)

```python
PropsSI('Tcrit', 'Water')          # 647.096 K
PropsSI('Pcrit', 'Water')          # 22.064 MPa
PropsSI('Ttriple', 'Water')        # 273.16 K
```

## Phase identification

```python
from CoolProp.CoolProp import PhaseSI
phase = PhaseSI('T', 300, 'P', 101325, 'Water')
# returns: 'liquid', 'gas', 'twophase', 'supercritical', ...
```

For a full list: see CoolProp docs (`PropsSI` source) or
```python
import CoolProp; print(CoolProp.CoolProp.get_input_pair_index('PT'))
```
