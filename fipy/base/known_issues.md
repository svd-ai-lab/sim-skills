# Known Issues — FiPy Driver

## `.solve` vs `.sweep`

**Status**: API design
**Description**: `eq.solve(var=phi, dt=dt)` does ONE linear solve.
For nonlinear (coefficient depends on unknown), use `eq.sweep(...)` in
a loop until residual converges.

## BC must be `constrain`, not in-place set

**Status**: API design
**Description**: `phi.value[0] = 1.0` does NOT pin the boundary value
during the solve — it just changes the cell value once. Use
`phi.constrain(1.0, mesh.facesLeft)`.

## ConvectionTerm coefficient is a FaceVariable

**Status**: API quirk
**Description**: `ConvectionTerm(coeff=u)` expects `u` to be a
`FaceVariable` (lives on faces). Passing a `CellVariable` silently
gives wrong results. Use `u.faceValue` or build directly as
`FaceVariable`.

## Solver fallback chain

**Status**: Performance
**Description**: FiPy tries PySparse → SciPy → PyAMG → Trilinos → PETSc.
If only SciPy is available, very large problems are slow. For HPC,
install petsc4py for parallel linear algebra.

## Time stepping is conditionally stable

**Status**: Math
**Description**: Explicit schemes (`ExplicitDiffusionTerm`) require
`dt < 0.5*dx²/D` (1D). Use implicit `DiffusionTerm` for unconditional
stability.

## CellVariable .value returns flat array

**Status**: Convention
**Description**: For 2D/3D, `phi.value` is shape `(numberOfCells,)`,
not `(nx, ny)`. Use `phi.value.reshape((ny, nx))` for plotting.

## No Gmsh msh4 support out of the box

**Status**: Bridge
**Description**: `Gmsh2D('foo.msh')` reads msh2 format. For msh4,
convert via meshio or save as msh2 from Gmsh.
