# Elmer FEM Solver Catalog

> Applies to: Elmer FEM 9.x–26.x

## Built-in solver libraries

Each `Solver N` block references a built-in (or user-written) solver via:

```
Procedure = "SharedObjectName" "EntryPoint"
```

### Physics solvers (common)

| Library | Entry | Physics | Variable |
|---------|-------|---------|----------|
| HeatSolve | HeatSolver | Heat conduction | Temperature |
| StressSolve | StressSolver | Linear elasticity | Displacement |
| FlowSolve | FlowSolver | Navier-Stokes | Flow Solution |
| MagnetoDynamics | MagnetoDynamicsCalcFields | Maxwell (induction) | Magnetic Vector Potential |
| StatElecSolver | StatElecSolver | Electrostatics | Potential |
| MeshSolve | MeshSolver | Mesh deformation | Mesh Update |
| AdvDiffusion | AdvectionDiffusionSolver | Scalar transport | User-named |
| SaveScalars | SaveScalars | Postprocess scalars | — |
| ResultOutputSolve | ResultOutputSolver | Write VTU / VTK | — |

### Typical HeatSolve setup

```
Solver 1
  Equation = Heat Equation
  Variable = Temperature
  Procedure = "HeatSolve" "HeatSolver"

  Linear System Solver = Iterative
  Linear System Iterative Method = BiCGStab
  Linear System Max Iterations = 500
  Linear System Convergence Tolerance = 1e-8
  Linear System Preconditioning = ILU0
  Linear System Residual Output = 10

  Nonlinear System Max Iterations = 1       ! linear problem
  Steady State Convergence Tolerance = 1e-5
End
```

### Typical StressSolver setup

```
Solver 1
  Equation = Linear Elasticity
  Variable = Displacement
  Variable DOFs = 2                         ! 2 for 2D, 3 for 3D
  Procedure = "StressSolve" "StressSolver"

  Linear System Solver = Direct
  Linear System Direct Method = Umfpack
End
```

Materials needed: `Youngs Modulus`, `Poisson Ratio`, `Density`.

### Typical FlowSolve setup (incompressible NS)

```
Solver 1
  Equation = Navier-Stokes
  Variable = Flow Solution[Velocity:2 Pressure:1]
  Procedure = "FlowSolve" "FlowSolver"

  Stabilization Method = P2/P1              ! or Bubbles, Stabilized
  Linear System Solver = Iterative
  Linear System Iterative Method = BiCGStab
End
```

## Linear solver options

```
Linear System Solver = Iterative | Direct | Multigrid
Linear System Iterative Method = BiCGStab | GMRES | CG | IDRS | TFQMR
Linear System Direct Method = Umfpack | MUMPS | Banded | Pardiso
Linear System Preconditioning = ILU0 | ILU1 | ILU2 | Diagonal | None
Linear System Max Iterations = 500
Linear System Convergence Tolerance = 1e-8
```

- **Iterative** is default, works for most problems
- **Direct** (Umfpack/MUMPS) for small problems or when Krylov stalls
- **Multigrid** for large Poisson-like problems

## Nonlinear / coupled loops

```
Nonlinear System Max Iterations = 20
Nonlinear System Convergence Tolerance = 1e-4
Nonlinear System Newton After Iterations = 3
Nonlinear System Relaxation Factor = 0.7

Steady State Convergence Tolerance = 1e-5
```

- Nonlinear loop: within each steady-state pass
- Steady-state loop: outer coupling between solvers

## SaveScalars (extract results)

```
Solver 2
  Exec Solver = After Timestep
  Equation = SaveScalars
  Procedure = "SaveData" "SaveScalars"
  Filename = "scalars.dat"

  Variable 1 = Temperature
  Operator 1 = max
  Variable 2 = Temperature
  Operator 2 = min
End
```

Writes a tab-separated file of requested scalar values per timestep —
useful for programmatic acceptance checks in sim.

## Execution order

```
Exec Solver = Always | Never | Before Timestep | After Timestep |
              Before Simulation | After Simulation | On
```

`Always` (default) runs the solver each steady-state / time iteration.

## Gotchas

- `Procedure = "Lib" "Func"` — two quoted strings, space-separated
- `Variable DOFs = N` — default 1; set to domain dimension for vector fields
- `Stabilization Method` important for convection-dominated problems
- Solver order matters: SaveScalars should come AFTER the physics solver
- `Active Solvers(N) = i1 i2 ... iN` in Equation lists must match solver indices
