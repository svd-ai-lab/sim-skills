# SU2 Config File Syntax

> Applies to: SU2 v8.x
> Last verified: 2026-04-14

## Grammar

```
% Comment line (starts with %)
KEYWORD= value                         % scalar
KEYWORD= ( value1, value2, value3 )    % list / tuple
KEYWORD= ( marker, param1, param2 )    % marker with params
```

- Case-insensitive on keyword names (`SOLVER` = `solver`)
- Whitespace around `=` is flexible
- Multi-value: parenthesized comma-separated

## Essential sections

### Physics / solver
```
SOLVER= EULER | NAVIER_STOKES | RANS | INC_EULER | INC_NAVIER_STOKES | ...
KIND_TURB_MODEL= SA | SST | NONE
MATH_PROBLEM= DIRECT | CONTINUOUS_ADJOINT | DISCRETE_ADJOINT
RESTART_SOL= NO | YES
```

### Freestream (compressible)
```
MACH_NUMBER= 0.8
AOA= 2.0
FREESTREAM_TEMPERATURE= 288.15
FREESTREAM_PRESSURE= 101325.0
REYNOLDS_NUMBER= 1e6
```

### Freestream (incompressible)
```
INC_DENSITY_MODEL= CONSTANT
INC_DENSITY_INIT= 998.2
INC_VELOCITY_INIT= ( 1.0, 0.0, 0.0 )
INC_TEMPERATURE_INIT= 288.15
```

### Mesh
```
MESH_FILENAME= mesh.su2
MESH_FORMAT= SU2 | CGNS | RECTANGLE | BOX
```

### Markers
```
MARKER_EULER= ( wall )                                  % slip wall
MARKER_HEATFLUX= ( wall, 0.0 )                         % no-slip adiabatic
MARKER_ISOTHERMAL= ( wall, 300.0 )
MARKER_FAR= ( farfield )                                % free-stream
MARKER_INLET= ( inlet, T_tot, P_tot, nx, ny, nz )
MARKER_OUTLET= ( outlet, P_static )
MARKER_SYM= ( sym )                                     % symmetry
MARKER_PERIODIC= ( per_low, per_high, ... )

MARKER_MONITORING= ( wall )    % compute coefficients (lift, drag) on these
MARKER_PLOTTING= ( wall )      % dump surface VTU for these
```

### Numerics / CFL
```
CFL_NUMBER= 5.0
CFL_ADAPT= YES
CFL_ADAPT_PARAM= ( 1.5, 0.5, 1.0, 100.0 )
LINEAR_SOLVER= FGMRES | BCGSTAB | RESTARTED_FGMRES
LINEAR_SOLVER_PREC= ILU | LU_SGS | JACOBI
LINEAR_SOLVER_ITER= 15
LINEAR_SOLVER_ERROR= 1e-6
```

### Convergence / iteration
```
ITER= 1000                              % max iterations
CONV_FIELD= RMS_DENSITY | LIFT | DRAG | ...
CONV_RESIDUAL_MINVAL= -8                % log10 threshold
CONV_CAUCHY_ELEMS= 100
CONV_CAUCHY_EPS= 1E-6
```

### Output
```
OUTPUT_FILES= ( RESTART, PARAVIEW, SURFACE_PARAVIEW )
VOLUME_OUTPUT= ( COORDINATES, SOLUTION, PRIMITIVE, RESIDUAL )
HISTORY_OUTPUT= ( RMS_RES, LIFT, DRAG, CAUCHY )
SCREEN_OUTPUT= ( INNER_ITER, WALL_TIME, RMS_RES )
WRT_SOL_FREQ= 100
WRT_CON_FREQ= 1
```

## Minimal working example (Euler)

```
SOLVER= EULER
MATH_PROBLEM= DIRECT
RESTART_SOL= NO

MACH_NUMBER= 0.5
AOA= 0.0
FREESTREAM_TEMPERATURE= 288.6
FREESTREAM_PRESSURE= 101300.0

MESH_FILENAME= mesh.su2
MESH_FORMAT= SU2

MARKER_EULER= ( upper_wall, lower_wall )
MARKER_INLET= ( inlet, 288.6, 102010.0, 1.0, 0.0, 0.0 )
MARKER_OUTLET= ( outlet, 101300.0 )
MARKER_MONITORING= ( lower_wall )

ITER= 200
CFL_NUMBER= 4.0
CONV_FIELD= RMS_DENSITY
CONV_RESIDUAL_MINVAL= -8
```

## Gotchas

- Marker names must exactly match those defined in the `.su2` mesh file
  (check `MARKER_TAG=` blocks in the mesh)
- `OUTPUT_FILES` defaults include restart + ParaView; override explicitly
  to reduce I/O in sweep runs
- For adjoint problems, `MATH_PROBLEM= DISCRETE_ADJOINT` requires a
  converged direct solution first (`RESTART_SOL= YES`)
- Comment character is `%` (not `#` or `//`)
