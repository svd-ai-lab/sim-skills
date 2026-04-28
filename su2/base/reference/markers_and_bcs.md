# SU2 Markers & Boundary Conditions

> Applies to: SU2 v8.x

## Marker name matching

Every `MARKER_*= ( name, ... )` in the config refers to a mesh tag
defined in the `.su2` file via `MARKER_TAG= <name>` blocks. Names are
case-sensitive. Typos produce silent BC misapplication.

Check mesh tags:
```
grep MARKER_TAG mesh.su2
```

## Compressible BCs

| Keyword | Physical meaning | Syntax |
|---------|------------------|--------|
| `MARKER_EULER` | Slip wall (inviscid) | `( w1, w2, ... )` |
| `MARKER_HEATFLUX` | No-slip with heat flux | `( wall, flux )` |
| `MARKER_ISOTHERMAL` | No-slip isothermal | `( wall, T )` |
| `MARKER_FAR` | Free-stream (Riemann) | `( farfield )` |
| `MARKER_INLET` | Total conditions inlet | `( inlet, T_tot, P_tot, nx, ny, nz )` |
| `MARKER_OUTLET` | Static pressure outlet | `( outlet, P_static )` |
| `MARKER_SYM` | Symmetry plane | `( sym )` |
| `MARKER_PERIODIC` | Periodic pair | `( donor, target, rot_center, rot_angle, translation )` |

## Incompressible BCs

| Keyword | Physical meaning |
|---------|------------------|
| `MARKER_INC_INLET_TYPE` | VELOCITY_INLET / PRESSURE_INLET |
| `MARKER_INC_OUTLET_TYPE` | PRESSURE_OUTLET |
| `INC_INLET_VELOCITY` | Inlet velocity vector |
| `MARKER_INC_OUTLET` | Outlet pressure |

## Post-processing markers

| Keyword | Purpose |
|---------|---------|
| `MARKER_MONITORING` | Integrate LIFT/DRAG/MOMENT over these surfaces |
| `MARKER_PLOTTING` | Write `surface_flow.vtu` for these |
| `MARKER_ANALYZE` | Extra aerodynamic coefficients |
| `MARKER_DESIGNING` | Adjoint shape-opt design markers |

## Typical bug: missing markers

If `grep MARKER_TAG mesh.su2` shows:
```
MARKER_TAG= airfoil
MARKER_TAG= farfield
```
then the .cfg MUST reference both OR explicitly ignore:
```
MARKER_EULER= ( airfoil )
MARKER_FAR= ( farfield )
```
Leaving one out produces a fatal "marker not found" error.

## Gotchas

- Names in `.su2` mesh are written by the mesh generator — check before
  editing .cfg
- For multi-airfoil / multi-body cases, list all walls in one marker:
  `MARKER_EULER= ( airfoil_a, airfoil_b )`
- Symmetry requires the plane to be aligned with a coordinate axis
