# CalculiX Analysis Types (Procedures)

> Applies to: CalculiX 2.11–2.20

## Supported procedures

| Keyword | Use | Output fields |
|---------|-----|---------------|
| `*STATIC` | Linear/nonlinear static | U (disp), S (stress), E (strain) |
| `*FREQUENCY, SOLVER=SPOOLES` | Modal analysis | Eigenmodes in .frd |
| `*BUCKLE` | Linear buckling | Buckling factors |
| `*HEAT TRANSFER [, STEADY STATE]` | Thermal conduction | NT (temperature), HFL (heat flux) |
| `*COUPLED TEMPERATURE-DISPLACEMENT` | Thermomechanical | U + NT |
| `*MODAL DYNAMIC` | Mode superposition transient | U(t), V(t), A(t) |
| `*STEADY STATE DYNAMICS` | Harmonic response | Amplitude + phase |
| `*VISCO` | Creep / viscoelasticity | U, CE (creep strain) |

## Skeleton per procedure

### Static
```
*STEP [, NLGEOM=YES]
*STATIC
<initial_inc>, <total_time>, <min_inc>, <max_inc>
*BOUNDARY
... (constraints)
*CLOAD / *DLOAD
... (loads)
*NODE PRINT, NSET=<set>
U
*EL PRINT, ELSET=<set>
S
*END STEP
```

### Frequency (modal)
```
*STEP
*FREQUENCY, SOLVER=SPOOLES
<n_modes>
*NODE FILE
U
*END STEP
```

### Heat transfer (steady)
```
*STEP
*HEAT TRANSFER, STEADY STATE
*BOUNDARY
<node/set>, 11, 11, <temperature>
*CFLUX / *DFLUX
<node/set>, 11, <flux>
*NODE PRINT, NSET=<set>
NT
*END STEP
```

## Choosing the right procedure

- **Static deformation under steady load** → `*STATIC`
- **Natural frequencies / mode shapes** → `*FREQUENCY`
- **Steady temperature field** → `*HEAT TRANSFER, STEADY STATE`
- **Buckling load factor** → `*BUCKLE`
- **Nonlinear material or large deformation** → `*STATIC, NLGEOM=YES`

## Limitations vs commercial solvers

- No explicit dynamics (`*DYNAMIC, EXPLICIT` is Abaqus-only)
- Limited contact (surface-to-surface is supported; self-contact limited)
- No automatic time stepping for creep
