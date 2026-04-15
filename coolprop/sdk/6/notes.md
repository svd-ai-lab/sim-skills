# CoolProp 6.x Notes

## Provenance

- Source: PyPI `CoolProp`
- Verified version: 6.4.1
- Compiled C++ kernel + Python bindings
- Bundled HEOS for ~120 pure fluids + humid air + most refrigerants

## Capabilities verified

| Feature | Status | Notes |
|---------|--------|-------|
| `PropsSI('H', 'T', 300, 'P', 1e5, 'Water')` | Verified | single-phase |
| `PropsSI('T', 'P', P, 'Q', 0, 'Water')` | Verified | saturation |
| `PropsSI('D', ..., 'R134a')` | Verified | refrigerants |

## Water-saturation benchmark @ 1 atm

T_sat = 373.124 K (textbook 373.124 K — exact)
h_fg  = 2.2565e6 J/kg (textbook 2.257e6 J/kg — 0.02% err)

## Version detection

```bash
python3 -c "import CoolProp; print(CoolProp.__version__)"
```
returns `6.4.1`. Driver normalizes to `6.4`.

## Optional companion packages

- `CoolProp.HumidAirProp.HAPropsSI` — psychrometric properties (built-in)
- `chemicals` — broader pure-component database (separate pip package)
- `fluids` — pipe flow / pumping (separate pip package)
