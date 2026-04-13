# CFX Solver Control Reference

## Convergence settings

```
SOLVER CONTROL:
  ADVECTION SCHEME:
    Option = High Resolution          # Recommended for most cases
    # OR
    Option = Upwind                   # More stable, less accurate
    # OR
    Option = Specified Blend Factor
    Blend Factor = 0.75
  END
  CONVERGENCE CONTROL:
    Maximum Number of Iterations = 200
    Minimum Number of Iterations = 1
    Timescale Control = Auto Timescale    # Recommended for steady state
    # OR
    Timescale Control = Physical Timescale
    Physical Timescale = 0.001 [s]
    # OR
    Timescale Factor = 5               # Multiplier for auto timescale
    Length Scale Option = Conservative   # More stable
  END
  CONVERGENCE CRITERIA:
    Residual Target = 1.E-5            # Standard target
    Residual Type = RMS                # Root-mean-square (recommended)
    # Conservation Target is optional (checks mass/momentum balance)
    Conservation Target = 0.01
  END
END
```

## Turbulence numerics

```
SOLVER CONTROL:
  Turbulence Numerics = High Resolution   # Or: First Order
END
```

## Compressible flow

```
SOLVER CONTROL:
  COMPRESSIBILITY CONTROL:
    High Speed Numerics = On           # Required for Ma > 0.3
  END
END
```

## Interrupt control (auto-stop on convergence)

```
SOLVER CONTROL:
  INTERRUPT CONTROL:
    Option = Any Interrupt
    CONVERGENCE CONDITIONS:
      Option = Default Conditions
    END
  END
END
```

## Physical timescale guidelines

| Flow type | Recommended timescale |
|-----------|----------------------|
| Incompressible pipe flow | L / U (domain length / inlet velocity) |
| External aerodynamics | 0.5 * L / U_freestream |
| Compressible | Auto Timescale with ramp-up |
| Turbomachinery | 1 / (N * n_blades) where N = RPM/60 |

## Convergence monitoring

Key residuals to watch in the `.out` file:
- **U-Mom, V-Mom, W-Mom**: Momentum equations
- **P-Mass**: Pressure-mass (continuity)
- **K-TurbKE**: Turbulent kinetic energy (SST/k-ε only)
- **O-TurbFreq**: Turbulent frequency (SST only)

### What "converged" means

| Criterion | Threshold | Meaning |
|-----------|-----------|---------|
| RMS residuals < target | 1e-5 (default) | Numerical convergence |
| Mass imbalance < 1% | Check IMBALANCE in monitor data | Conservation satisfied |
| Monitor points stable | No oscillation in last 20% of iterations | Physical convergence |
| Forces/moments stable | Drag/lift coefficient plateaued | Engineering quantities converged |

### Convergence troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Residuals stall > 1e-3 | Poor mesh quality | Refine mesh, check y+ |
| Residuals oscillate | Timescale too aggressive | Reduce timescale factor, use Physical Timescale |
| P-Mass diverges | Incompatible BCs | Check mass flow balance inlet vs outlet |
| TurbKE/TurbFreq diverge | Bad initialization | Use lower turbulence intensity, ramp up |
