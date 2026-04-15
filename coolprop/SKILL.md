---
name: coolprop-sim
description: Use when driving CoolProp (open-source thermophysical-property database, REFPROP-equivalent for ~120 pure fluids + humid air) via Python scripts — enthalpy / entropy / density / viscosity / saturation curves / Helmholtz EoS lookups for thermodynamic cycle analysis, HVAC, refrigeration, power plants — through sim runtime one-shot execution.
---

# coolprop-sim

You are connected to **CoolProp** via sim-cli.

CoolProp (Bell et al., IECR 2014) is the open-source equivalent of NIST
REFPROP: high-accuracy thermophysical properties via Helmholtz-energy
EoS for ~120 pure fluids + humid-air psychrometrics + transport
properties. Pip-installable (`pip install CoolProp`); ships compiled
C++ kernel.

Scripts are plain `.py`:

```python
from CoolProp.CoolProp import PropsSI
T_sat = PropsSI('T', 'P', 101325, 'Q', 0, 'Water')   # 373.124 K
h     = PropsSI('H', 'T', 300, 'P', 1e5, 'R134a')
mu    = PropsSI('V', 'T', 300, 'P', 1e5, 'Air')      # viscosity
```

Same subprocess driver mode as PyBaMM / Cantera.

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/workflow.md` | PropsSI signature, common queries, SI units throughout. |
| `base/reference/properties.md` | Property codes (T, P, H, S, D, U, V, L, C, ...). |
| `base/reference/states.md` | State pair patterns (TP, PQ, TQ, HP, ...). |
| `base/reference/mixtures.md` | Pseudo-pure mixtures via "REFPROP::" prefix or HEOS::Mixtures. |
| `base/snippets/01_water_props.py` | Verified water saturation + h_fg E2E. |
| `base/known_issues.md` | All SI; case-sensitive fluid names; humid air via HAPropsSI. |

## sdk/6/ — CoolProp 6.x

- `sdk/6/notes.md` — version-specific surface notes.

---

## Hard constraints

1. **All inputs and outputs are SI** — Pa, K, J/kg, kg/m³, Pa·s, ...
   No psia, no °F, no kJ. Convert at the boundary.
2. **Property codes are case-sensitive single letters or short strings**:
   `T` (temperature), `P` (pressure), `H` (enthalpy), `S` (entropy),
   `D` (density), `Q` (vapor quality 0..1), `V` (viscosity), `L`
   (thermal conductivity), `C` (cp), `O` (cv).
3. **Exactly two state inputs needed** for single-phase queries; for
   saturation curves, use `(P, Q)` or `(T, Q)` with Q ∈ [0, 1].
4. **Acceptance != "ran without error"**. Validate against textbook /
   NIST values (water at 1 atm: T_sat = 373.124 K, h_fg = 2.257e6 J/kg).
5. **Print results as JSON on the last stdout line.**
6. **Humid-air psychrometrics need `HAPropsSI`** (different signature) —
   `HAPropsSI('H', 'T', 300, 'P', 101325, 'R', 0.5)` for relative humidity.

---

## Required protocol

1. Gather inputs:
   - **Category A:** fluid (or mixture), state pair, target property,
     acceptance.
   - **Category B:** evaluation grid resolution if scanning a curve.
2. `sim check coolprop`.
3. Write `.py` per `base/reference/workflow.md`.
4. `sim lint script.py`.
5. `sim run script.py --solver coolprop`.
6. Validate JSON.
