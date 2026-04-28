# SU2 Solver Families

> Applies to: SU2 v8.x

## Compressible flow

| SOLVER= | Physics | Typical use |
|---------|---------|-------------|
| `EULER` | Inviscid compressible | Wave / shock, aerodynamic preliminary |
| `NAVIER_STOKES` | Laminar compressible | Low-Re laminar |
| `RANS` | Turbulent compressible | External aero, high-Re airfoils |

With `RANS`:
```
KIND_TURB_MODEL= SA    % Spalart-Allmaras (default)
                 | SST % Shear stress transport (k-omega)
```

## Incompressible flow

| SOLVER= | Physics |
|---------|---------|
| `INC_EULER` | Inviscid incompressible |
| `INC_NAVIER_STOKES` | Laminar incompressible |
| `INC_RANS` | Turbulent incompressible |

```
INC_DENSITY_MODEL= CONSTANT | BOUSSINESQ | VARIABLE
INC_ENERGY_EQUATION= YES | NO
```

## Other solvers

| SOLVER= | Purpose |
|---------|---------|
| `HEAT_EQUATION` | Pure heat conduction |
| `ELASTICITY` | Linear / non-linear structural |
| `FEM_EULER` / `FEM_NAVIER_STOKES` | DG-FEM variants |
| `MULTIPHYSICS` | Multi-zone coupled |

## Math problem types

```
MATH_PROBLEM= DIRECT                    % forward solve
MATH_PROBLEM= CONTINUOUS_ADJOINT        % analytic adjoint for design
MATH_PROBLEM= DISCRETE_ADJOINT          % AD-based adjoint (requires autodiff build)
```

## Common numerics by solver

| Solver | Default CFL | Convective | Time integration |
|--------|-------------|------------|------------------|
| Euler | 4-10 | JST / ROE | Implicit Euler |
| RANS-SA | 2-5 | ROE + MUSCL | Implicit Euler |
| RANS-SST | 1-3 | AUSM | Implicit Euler |
| Inc_NS | 10-50 | FDS | SIMPLE-like |

## When to use what

- **Inviscid Euler**: early-stage aero, shock tubes, simple channel flows
- **Laminar NS**: low-Re (< 10^3), heat transfer verification cases
- **RANS-SA**: external aero, airfoils, wings — simple, fast
- **RANS-SST**: separated flows, adverse pressure gradients
- **DISCRETE_ADJOINT**: optimization, sensitivity analysis (needs AD build)
- **INC_***: incompressible water/oil flows, Ma < 0.3

## Multi-zone

Pseudo-grammar:
```
SOLVER= MULTIPHYSICS
CONFIG_LIST= ( fluid.cfg, solid.cfg )
MARKER_ZONE_INTERFACE= ( fluid_interface, solid_interface )
```

Each zone has its own `.cfg`; the top-level orchestrates coupling.
