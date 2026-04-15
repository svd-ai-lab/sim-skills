# Pyomo 6.x Notes

## Provenance

- Source: PyPI `pyomo`
- Verified version: 6.6.2
- LP backend verified: `highspy` (HiGHS 1.5.3) via `appsi_highs`

## Capabilities verified

| Feature | Status | Notes |
|---------|--------|-------|
| `ConcreteModel` | Verified | |
| `Var(within=NonNegativeReals)` | Verified | |
| `Objective(sense=maximize)` | Verified | |
| `Constraint(expr=...)` | Verified | |
| `SolverFactory('appsi_highs')` | Verified | requires highspy |
| `.solve(m)` | Verified | returns LegacySolverResults |
| `pyo.value(m.x)` | Verified | result extraction |

## Classic LP benchmark

`max 3x+5y, x≤4, 2y≤12, 3x+2y≤18, x,y≥0` → (2, 6), obj=36
(matches textbook to machine precision via HiGHS).

## Version detection

```bash
python3 -c "import pyomo; print(pyomo.__version__)"
```
returns `6.6.2`. Driver normalizes to `6.6`.

## Recommended pip-only stack

```bash
pip install pyomo highspy        # LP/MIP via HiGHS — pure Python install
```

For NLP, `ipopt` requires a system install or conda; pure-pip options
for nonlinear are limited.
