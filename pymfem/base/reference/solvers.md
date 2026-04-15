# MFEM Linear Solvers

> Applies to: MFEM 4.8 (serial)

## Direct solvers

### UMFPackSolver
Robust LU-based sparse direct. Best for problems < 100k DOFs.

```python
solver = mfem.UMFPackSolver()
solver.SetOperator(A)
solver.Mult(B, X)
```

Dependency: MFEM must be built with SuiteSparse. PyMFEM pip wheel
usually includes it.

### Gaussian elimination
Fallback for very small systems:

```python
A_dense = A.ToDenseMatrix()
A_inv = mfem.DenseMatrix()
A_dense.Invert()
A_inv = A_dense   # now A_inv ≈ A⁻¹; X = A_inv · B
```

## Iterative solvers

### PCG (preconditioned conjugate gradient)
For symmetric positive-definite systems (Poisson, elasticity with
proper BCs).

```python
M = mfem.GSSmoother(A)                      # Gauss-Seidel preconditioner
# or M = mfem.DSmoother(A) for Jacobi
mfem.PCG(A, M, B, X,
         print_iter=1,                       # verbosity 0..2
         max_num_iter=2000,
         RTOLERANCE=1e-12, ATOLERANCE=0.0)
```

### GMRES
For non-symmetric systems (advection, non-SPD).

```python
gmres = mfem.GMRESSolver()
gmres.SetOperator(A)
gmres.SetPreconditioner(M)
gmres.SetRelTol(1e-10)
gmres.SetMaxIter(2000)
gmres.SetPrintLevel(1)
gmres.Mult(B, X)
```

### BiCGStab
Non-symmetric, often cheaper than GMRES for large problems.

```python
bicg = mfem.BiCGSTABSolver()
bicg.SetOperator(A)
bicg.SetPreconditioner(M)
bicg.Mult(B, X)
```

## Preconditioners

| Preconditioner | Best for | Cost |
|----------------|----------|------|
| `GSSmoother` | Poisson, diffusion | O(nnz) |
| `DSmoother` | Mass matrices | O(n) |
| `UMFPackSolver` | As exact preconditioner | O(direct) |

For parallel (PyMFEM .par module only):
- `HypreBoomerAMG` — AMG for Poisson-like, excellent scaling
- `HypreAMS` — Auxiliary Maxwell for H(curl) problems
- `HypreADS` — Auxiliary Divergence for H(div)

## Choosing a solver

```
Problem size:
  < 10k DOFs    → UMFPackSolver (direct)
  10k - 1M      → PCG + GSSmoother (if SPD) or GMRES
  > 1M          → switch to mfem.par + HypreBoomerAMG

Symmetry:
  SPD (Poisson, heat, elasticity with Dirichlet)  → PCG
  Non-symmetric (advection, Navier-Stokes)        → GMRES / BiCGStab

Robustness need:
  Flaky convergence   → Direct (UMFPack)
  Performance critical → Iterative + tuned preconditioner
```

## Convergence monitoring

```python
bicg = mfem.BiCGSTABSolver()
bicg.SetOperator(A)
bicg.SetPrintLevel(1)        # 0=silent, 1=final, 2=every iter
bicg.SetRelTol(1e-10)
bicg.Mult(B, X)
# Check:
print("Converged:", bicg.GetConverged())
print("Iterations:", bicg.GetNumIterations())
print("Final residual:", bicg.GetFinalNorm())
```

## Gotchas

- `UMFPackSolver` requires SuiteSparse at build time. Check with
  `hasattr(mfem, 'UMFPackSolver')`. Fall back to PCG + GSSmoother if not.
- PCG assumes SPD; using on non-SPD diverges silently
- `SetOperator(A)` must be called BEFORE `Mult(B, X)`
- Some solvers modify B during solve — pass a copy if B is needed after
