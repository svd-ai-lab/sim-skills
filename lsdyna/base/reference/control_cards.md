# LS-DYNA Control Cards

## Essential control cards

### *CONTROL_TERMINATION
Defines when the analysis ends.
```
*CONTROL_TERMINATION
$  ENDTIM    ENDCYC     DTMIN    ENDENG    ENDMAS
   1.0E-3         0       0.0       0.0 1.0000E+8
```
- `ENDTIM`: End time (required for explicit)
- `ENDCYC`: Max cycle count (0=no limit)
- `DTMIN`: Min timestep — terminates if dt drops below this
- `ENDMAS`: Max added mass percentage for mass scaling

### *CONTROL_TIMESTEP
Controls explicit timestep calculation.
```
*CONTROL_TIMESTEP
$  DTINIT    TSSFAC      ISDO    TSLIMT     DT2MS      LCTM     ERODE     MS1ST
       0.0       0.9         0       0.0       0.0         0         0         0
```
- `TSSFAC`: Timestep scale factor (default 0.9, range 0.0-1.0). Lower = more stable, slower.
- `DT2MS`: Mass scaling target timestep. **Warning**: adds artificial mass — changes physics.
- `DTINIT`: Override initial timestep (0.0 = automatic)

### *CONTROL_ENERGY
Energy dissipation options.
```
*CONTROL_ENERGY
$    HGEN      RWEN    SLNTEN     RYLEN
         2         2         2         2
```
- `HGEN=2`: Include hourglass energy in energy balance
- `RWEN=2`: Include Rayleigh damping energy
- `SLNTEN=2`: Include sliding interface energy
- `RYLEN=2`: Include stonewall energy

## Implicit solver cards

### *CONTROL_IMPLICIT_GENERAL
Activates implicit solver.
```
*CONTROL_IMPLICIT_GENERAL
$  IMFLAG       DT0    IMFORM      NSBS       IGS     CNSTN      FORM    ZERO_V
         1   1.0E-3         2         1         2         0         0         0
```
- `IMFLAG=1`: Enable implicit
- `DT0`: Initial implicit timestep
- `IMFORM=2`: Direct linear solver

### *CONTROL_IMPLICIT_SOLUTION
Nonlinear solution parameters.
```
*CONTROL_IMPLICIT_SOLUTION
$  NSOLVR    ILIMIT    MAXREF     DCTOL     ECTOL     RCTOL     LSTOL    ABSTOL
        12        11       200   1.0E-3   1.0E-2   1.0E+10       0.9   1.0E-10
```
- `NSOLVR=12`: BFGS solver
- `ILIMIT`: Max iterations per step
- `DCTOL`: Displacement convergence tolerance
- `ECTOL`: Energy convergence tolerance

## Database output cards

### *DATABASE_BINARY_D3PLOT
Binary plot database output interval.
```
*DATABASE_BINARY_D3PLOT
$       DT
   1.0E-4
```

### *DATABASE_GLSTAT
Global statistics (energies, velocities, timestep).
```
*DATABASE_GLSTAT
$       DT
   1.0E-5
```

### *DATABASE_EXTENT_BINARY
Controls what data is written to d3plot.
```
*DATABASE_EXTENT_BINARY
$   NEIPH     NEIPS    MAXINT    STRFLG    SIGFLG    EPSFLG    RLTFLG    ENGFLG
         0         0         3         1         1         1         1         1
```

## Boundary conditions

### *BOUNDARY_SPC_NODE
Single-point constraint on individual nodes.
```
*BOUNDARY_SPC_NODE
$    NID       CID      DOFX      DOFY      DOFZ     DOFRX     DOFRY     DOFRZ
       1         0         1         1         1         0         0         0
```
- DOF value: 1=constrained, 0=free
- CID: Coordinate system ID (0=global)

### *BOUNDARY_SPC_SET
Constraint applied to a node set.
```
*BOUNDARY_SPC_SET
$     NSID       CID      DOFX      DOFY      DOFZ     DOFRX     DOFRY     DOFRZ
         1         0         1         1         1         0         0         0
```

## Loading

### *LOAD_NODE_POINT
Point load on individual nodes.
```
*LOAD_NODE_POINT
$    NID       DOF      LCID        SF       CID
       5         3         1    100.0         0
```
- DOF: 1=X, 2=Y, 3=Z
- LCID: Load curve ID
- SF: Scale factor

### *DEFINE_CURVE
Time-dependent load curve.
```
*DEFINE_CURVE
$     LCID      SIDR       SFA       SFO      OFFA      OFFO    DATTYP
         1         0       1.0       1.0       0.0       0.0         0
$                 A1                  O1
               0.000               0.000
            1.0E-4               1.000
            1.0E-3               1.000
```
- Pairs of (time, value) follow the header card
- SFA/SFO: Scale factors for abscissa/ordinate
