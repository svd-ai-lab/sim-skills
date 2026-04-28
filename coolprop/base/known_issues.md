# Known Issues — CoolProp Driver

## All inputs and outputs are SI

**Status**: Convention
**Description**: Pa not psia, K not °C/°F, J/kg not kJ/kg or Btu/lb.
Converting at the boundary is the user's responsibility.

## Fluid names are case-sensitive

**Status**: API
**Description**: `'Water'`, `'R134a'`, `'Methane'`, `'CO2'`. Wrong case
raises `ValueError: Bad fluid name`. Use exact strings from
[CoolProp's fluid table](http://www.coolprop.org/fluid_properties/PurePseudoPure.html).

## Two-phase region requires Q in input pair

**Status**: API
**Description**: For saturation, you MUST provide vapor quality Q
(0 = saturated liquid, 1 = saturated vapor). `PropsSI('T', 'P', P, 'H', h)`
inside the dome may return inconsistent values without Q.

## Humid air is a different function

**Status**: API design
**Description**: `PropsSI` works on pure fluids and HEOS mixtures.
For humid-air psychrometrics (RH, wet-bulb T, etc.), use
`from CoolProp.HumidAirProp import HAPropsSI` with its own signature.

## Compressed-water enthalpy reference

**Status**: Convention
**Description**: CoolProp's enthalpy reference for pure water is
the IAPWS choice (h=0 at triple-point liquid). Other tables may use
different references — compare DELTAS, not absolute h, when cross-
checking.

## Vectorized PropsSI returns NumPy arrays

**Status**: Convenience
**Description**: Pass NumPy arrays for any input → array output.
`json.dumps` won't accept np.float64 — wrap with `float(...)` or
`.tolist()` before serializing.

## Numerical artefacts at critical / triple points

**Status**: Math
**Description**: Near critical point, derivatives diverge → small
input perturbations give large output changes. Stay >5 K away from
T_crit and >1% pressure offset for stable evaluations.
