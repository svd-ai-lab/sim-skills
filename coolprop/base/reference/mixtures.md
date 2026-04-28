# Mixtures

CoolProp supports mixtures via two backends:

## HEOS (Helmholtz EoS) — pure-pip default

```python
PropsSI('T', 'P', 5e6, 'Q', 0, 'HEOS::Methane[0.5]&Ethane[0.5]')
```

Format: `HEOS::Fluid1[mole_frac1]&Fluid2[mole_frac2]&...`

## REFPROP — requires NIST REFPROP installation

```python
PropsSI('T', 'P', 5e6, 'Q', 0, 'REFPROP::METHANE[0.5]&ETHANE[0.5]')
```

Only available if NIST REFPROP DLL is on path; out of scope for
pure-pip install.

## Predefined mixtures

```python
PropsSI('T', 'P', 1e5, 'Q', 0, 'Air.mix')            # standard air mixture
PropsSI('T', 'P', 1e5, 'Q', 0, 'R407C.mix')          # refrigerant blend
```

## Caveats

- HEOS mixtures need binary interaction parameters; many pairs are
  implemented but not all. Calls that fail raise a clear error.
- For mixtures, `T_sat` is replaced by bubble point (Q=0) and dew
  point (Q=1) — they are NOT equal at fixed P (zeotropic glide).
