# Elmer SIF Block Structure

> Applies to: Elmer FEM 9.x–26.x

## Block anatomy

Elmer `.sif` files are composed of **named blocks** delimited by `End`:

```
BlockName [Index]
  Key = Value
  Vector Key(N) = v1 v2 ... vN
End
```

- Comments start with `!`
- Key names are case-insensitive (convention: `Title Case`)
- Blocks are whitespace-delimited, typically 2-space indent

## Required blocks

### Header
```
Header
  CHECK KEYWORDS Warn                        ! optional keyword-check
  Mesh DB "." "meshname"                     ! mesh dir (. = cwd)
  Include Path ""
  Results Directory ""
End
```

### Simulation
```
Simulation
  Max Output Level = 5                        ! 0-10 verbosity
  Coordinate System = Cartesian               ! or Axi Symmetric, Cylindric
  Simulation Type = Steady State              ! or Transient, Scanning
  Steady State Max Iterations = 1
  Output Intervals = 1
  Timestepping Method = BDF                   ! for Transient
  BDF Order = 1
  Post File = "case.vtu"                      ! output filename
  Output File = "case.result"
End
```

### Constants (optional but common)
```
Constants
  Gravity(4) = 0 -1 0 9.82                    ! direction + magnitude
  Stefan Boltzmann = 5.67e-8
  Permittivity of Vacuum = 8.8542e-12
End
```

### Body
```
Body 1
  Target Bodies(1) = 1                        ! which mesh body IDs
  Name = "Fluid"
  Equation = 1                                ! which Equation block
  Material = 1                                ! which Material block
  Body Force = 1                              ! optional: which Body Force
  Initial Condition = 1                       ! optional
End
```

### Material
```
Material 1
  Name = "Water"
  Density = 1000.0
  Viscosity = 1e-3
  Heat Conductivity = 0.6
  Heat Capacity = 4186
  ! ... many more depending on physics
End
```

### Equation
```
Equation 1
  Name = "HeatFlow"
  Active Solvers(1) = 1                       ! list solvers by index
End
```

### Solver
```
Solver 1
  Equation = Heat Equation                    ! built-in equation name
  Variable = Temperature                      ! unknown name
  Procedure = "HeatSolve" "HeatSolver"        ! shared object + entry point

  Linear System Solver = Iterative            ! or Direct
  Linear System Iterative Method = BiCGStab   ! or GMRES, CG
  Linear System Max Iterations = 500
  Linear System Convergence Tolerance = 1e-8
  Linear System Preconditioning = ILU0

  Nonlinear System Max Iterations = 1         ! for linear problems
  Nonlinear System Convergence Tolerance = 1e-5

  Steady State Convergence Tolerance = 1e-5
End
```

### Boundary Condition
```
Boundary Condition 1
  Target Boundaries(1) = 1                    ! boundary ID from mesh
  Name = "Cold Wall"
  Temperature = 0.0                           ! Dirichlet
  ! Heat Flux = 1000.0                        ! Neumann alternative
End
```

### Body Force (optional)
```
Body Force 1
  Heat Source = 10000.0
End
```

### Initial Condition (optional, for Transient)
```
Initial Condition 1
  Temperature = 293.15
End
```

## Block numbering

Blocks are referenced by **integer index** (matches `Body.Material =
<idx>`). The index comes from either explicit numbering (`Body 1`,
`Body 2`) or automatically from the block order.

## Gotchas

- Missing `End` causes cryptic parse errors far from the source
- `CHECK KEYWORDS Warn` in Header enables helpful typo warnings
- Vector syntax: `Key(N) = v1 v2 ... vN` — count must match actual count
- String values use `"double quotes"`, not single quotes
- `Mesh DB "." "meshname"` means `./meshname/mesh.*` files
- `Max Output Level` below 4 suppresses useful info
