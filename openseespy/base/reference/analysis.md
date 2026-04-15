# Analysis options — system / numberer / constraints / integrator / algorithm / analysis

The full chain is **mandatory**. OpenSees raises "analysis object not
constructed" if any link is missing.

## system — sparse matrix storage

| Choice | Use when |
|---|---|
| `BandSPD` | symmetric positive definite (linear elastic statics, eigen) |
| `BandGen` | general non-symmetric or sign-indefinite (with `geomTransf` PDelta) |
| `UmfPack` | large sparse, robust direct solve |
| `SparseSYM` / `SparseGEN` | medium sparse |
| `Mumps` | parallel direct (MPI builds only) |

## numberer — DOF ordering

| Choice | Notes |
|---|---|
| `Plain` | sequential, simplest, slow on large models |
| `RCM` | Reverse-Cuthill-McKee — minimizes bandwidth, recommended default |
| `AMD` | Approximate Minimum Degree — best for sparse direct |

## constraints — how MP/SP constraints enter

| Choice | When |
|---|---|
| `Plain` | only homogeneous SPs (`fix`); cheapest |
| `Transformation` | rigid links / equalDOF |
| `Penalty` | inequality / hard contact (needs alpha tuning) |
| `Lagrange` | exact MP enforcement, adds Lagrange DOFs |

## integrator — load increment / time stepping

Static:
- `LoadControl(dlambda)` — increments load by `dlambda` each step
- `DisplacementControl(node, dof, dU)` — increments displacement
- `ArcLength(s, alpha)` — for snap-through / post-buckling

Transient:
- `Newmark(gamma, beta)` — default `0.5, 0.25` (constant average accel)
- `HHT(alpha)` — numerical damping for stiff problems
- `CentralDifference` — explicit, conditionally stable

## algorithm — equilibrium iteration

| Choice | Use when |
|---|---|
| `Linear` | linear elastic; one-shot solve |
| `Newton` | standard nonlinear |
| `KrylovNewton` | line-search, faster for ill-conditioned |
| `BFGS` / `Broyden` | quasi-Newton, no tangent reformulation each iter |
| `NewtonLineSearch` | for soft convergence |

`test('NormDispIncr', tol, max_iter)` should be set for nonlinear.

## analysis — top-level driver

- `Static` — incremental static
- `Transient` — direct integration in time
- `VariableTransient` — adaptive Δt
- `EigenAnalysis` — implicit; just call `ops.eigen(N)` after the chain
