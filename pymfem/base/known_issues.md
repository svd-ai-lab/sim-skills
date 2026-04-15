# Known Issues — PyMFEM Driver

## UMFPackSolver availability varies

**Status**: Runtime check
**Description**: PyMFEM pip wheel usually includes SuiteSparse for
UMFPack, but not always. Scripts should feature-detect:
```python
if hasattr(mfem, "UMFPackSolver"):
    solver = mfem.UMFPackSolver()
else:
    solver = mfem.GSSmoother(A)  # iterative fallback
```

## FormLinearSystem mutates its out-args

**Status**: MFEM convention
**Description**: `a.FormLinearSystem(ess_tdof, x, b, A, X, B)` fills
A, X, B in place. Callers must construct them as empty MFEM types
(`SparseMatrix()`, `Vector()`) before calling. Passing wrong types
(e.g., a numpy array) silently fails or segfaults.

## `x.Assign(value)` sets Dirichlet value

**Status**: Non-intuitive
**Description**: The GridFunction `x` passed to FormLinearSystem is
used to provide the Dirichlet boundary values. Its pre-solve values at
essential DOFs become the BC. For homogeneous BCs, `x.Assign(0.0)`
before the call.

## Variable coefficients via PyCoefficient are slow

**Status**: Python/C++ crossing cost
**Description**: `mfem.PyCoefficient.EvalValue` runs in Python at every
quadrature point. For dense meshes, this dominates runtime. For static
coefficients, precompute onto a GridFunction and use
`GridFunctionCoefficient`.

## `ess_tdof_list` type is `intArray` not `list`

**Status**: MFEM type
**Description**: `intArray([1, 2, 3])` works but `[1, 2, 3]` directly
passed to FormLinearSystem does not. Always wrap Python lists.

## Pip wheel is large (~60-150 MB)

**Status**: Install-time
**Description**: Normal for a packaged C++ library. First pip install
takes 1-2 minutes.

## No direct `.frd` or `.msh` read

**Status**: Bridge via meshio
**Description**: MFEM reads its own `.mesh` format, and `.vtk`.
Convert other formats via meshio first.
