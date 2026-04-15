# Cantera 2.x Notes

## Provenance

- Source: PyPI `cantera`
- Verified version: 2.6.0a3
- Bundled mechanisms: `gri30.yaml`, `h2o2.yaml`, `air.yaml`, `airNASA9.yaml`

## Capabilities verified

| Feature | Status | Notes |
|---------|--------|-------|
| `Solution('gri30.yaml')` | Verified | bundled mechanism |
| `g.TPX = T, P, X` | Verified | tuple setter |
| `g.equilibrate('HP')` | Verified | adiabatic, const P |
| `g.X / g.Y / g.T / g.P` | Verified | property accessors |
| `g['CO2'].X` | Verified | per-species lookup |

## Adiabatic flame benchmark

CH4/air, φ=1, 300 K, 1 atm, equilibrate('HP') → T_ad = **2225.5 K**
(textbook 2225 K, error 0.5 K).

## Version detection

```bash
python3 -c "import cantera as ct; print(ct.__version__)"
```
returns `2.6.0a3`. Driver normalizes to short form `2.6`.

## API differences vs 3.x (forward-compat note)

- 3.x renames `Quantity` constructor args; 2.6 form still works as deprecated.
- 3.x adds `kinetics_model` parameter to `Solution`; default unchanged.
- Reactor / ReactorNet API is stable across 2.6 → 3.x.
