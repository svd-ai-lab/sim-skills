# SU2 Output, History & Restart

> Applies to: SU2 v8.x

## Output file zoo

| File | Purpose | Toggled by |
|------|---------|-----------|
| `history.csv` | Per-iteration convergence | always |
| `restart_flow.dat` | Binary restart (for RESTART_SOL=YES) | `RESTART` in OUTPUT_FILES |
| `flow.vtu` | Volume ParaView | `PARAVIEW` in OUTPUT_FILES |
| `surface_flow.vtu` | Surface ParaView | `SURFACE_PARAVIEW` |
| `forces_breakdown.dat` | Aerodynamic coefficients text | always for compressible |
| `config_CFD.cfg` | Echo of parsed config | always |

Toggle:
```
OUTPUT_FILES= ( RESTART, PARAVIEW, SURFACE_PARAVIEW, SURFACE_CSV )
```

Skip VTU (faster sweeps):
```
OUTPUT_FILES= ( RESTART )
```

## history.csv schema

Default columns (varies by solver):
```
"Time_Iter", "Outer_Iter", "Inner_Iter",
"rms[Rho]", "rms[RhoU]", "rms[RhoV]", "rms[RhoE]",
"LIFT", "DRAG", "SIDEFORCE", "CMx", "CMy", "CMz",
"LinSolIter", "LinSolRes", "CFL_NUMBER"
```

Enable monitored coefficients:
```
HISTORY_OUTPUT= ( RMS_RES, AERO_COEFF, CAUCHY )
```

Screen subset:
```
SCREEN_OUTPUT= ( INNER_ITER, RMS_RES, LIFT, DRAG )
```

## Convergence criteria

### Residual-based (default)
```
CONV_FIELD= RMS_DENSITY
CONV_RESIDUAL_MINVAL= -8           % log10 threshold; stop when rms<1e-8
```

### Cauchy-based (for lift/drag)
```
CONV_FIELD= LIFT
CONV_CAUCHY_ELEMS= 100
CONV_CAUCHY_EPS= 1E-6              % stop when rolling stddev(LIFT) < eps
```

### Combined
```
CONV_FIELD= ( RMS_DENSITY, LIFT )
```

## Restart

```
RESTART_SOL= NO    % cold start
% OR
RESTART_SOL= YES   % reads restart_flow.dat from cwd
RESTART_ITER= 100  % for unsteady
```

Useful pattern: cold-start to 50% convergence, then restart with tighter
CFL / adjoint from the saved state.

## Post-processing

`SU2_SOL` reads the restart + mesh and writes VTUs:
```
SU2_SOL config.cfg
```
Useful when `PARAVIEW` was disabled in the solve run.

## Parsing history.csv (Python)

```python
import csv
with open("history.csv", newline="") as f:
    reader = csv.reader(f)
    header = [c.strip().strip('"') for c in next(reader)]
    rows = list(reader)
final_rms = float(rows[-1][header.index("rms[Rho]")])
```

Acceptance example:
```python
assert -10 < final_rms < -2    # dropped at least 1 order from ~-1.4 start
```

## Gotchas

- CSV header strings are **space-padded** quoted — always `.strip().strip('"')`
- `history.csv` in some versions uses `.dat` extension — check
- `forces_breakdown.dat` plain-text, grep-friendly
- `SURFACE_CSV` format: `x,y,z,Pressure_Coefficient,Skin_Friction_Coefficient_...`
