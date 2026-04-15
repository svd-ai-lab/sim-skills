# PyMFEM Workflow

> Applies to: PyMFEM 4.8

## Canonical script skeleton

```python
import mfem.ser as mfem

# 1. MESH
mesh = mfem.Mesh(nx, ny, "TRIANGLE", True, 1.0, 1.0)
# or load from file: mesh = mfem.Mesh("model.mesh")
dim = mesh.Dimension()

# 2. FE SPACE
fec = mfem.H1_FECollection(order=1, dim=dim)
fespace = mfem.FiniteElementSpace(mesh, fec)
# vector-valued field: fespace = mfem.FiniteElementSpace(mesh, fec, dim)

# 3. ESSENTIAL BOUNDARY DOFs (Dirichlet)
ess_tdof_list = mfem.intArray()
ess_bdr = mfem.intArray([1] * mesh.bdr_attributes.Max())
fespace.GetEssentialTrueDofs(ess_bdr, ess_tdof_list)

# 4. FORMS
# Linear (RHS)
b = mfem.LinearForm(fespace)
b.AddDomainIntegrator(mfem.DomainLFIntegrator(coefficient_f))
b.Assemble()

# Bilinear (LHS)
a = mfem.BilinearForm(fespace)
a.AddDomainIntegrator(mfem.DiffusionIntegrator(coefficient_k))
a.Assemble()

# 5. SOLUTION GridFunction
x = mfem.GridFunction(fespace)
x.Assign(0.0)        # Dirichlet value

# 6. FORM LINEAR SYSTEM (apply BCs)
A = mfem.SparseMatrix()
B = mfem.Vector()
X = mfem.Vector()
a.FormLinearSystem(ess_tdof_list, x, b, A, X, B)

# 7. SOLVE
solver = mfem.UMFPackSolver()   # direct
solver.SetOperator(A)
solver.Mult(B, X)
# Or PCG:
# M = mfem.GSSmoother(A)
# mfem.PCG(A, M, B, X, print_iter=0, max_num_iter=2000, RTOLERANCE=1e-12, ATOLERANCE=0.0)

# 8. RECOVER SOLUTION
a.RecoverFEMSolution(X, b, x)

# 9. USE x (e.g., get numpy array via x.GetDataArray())
print("max:", float(x.GetDataArray().max()))
```

## Mesh constructors

```python
# Built-in:
mfem.Mesh(nx, ny, "TRIANGLE", generate_edges=True, sx=1.0, sy=1.0)
mfem.Mesh(nx, ny, "QUADRILATERAL", ...)
mfem.Mesh(nx, ny, nz, "TETRAHEDRON", ...)
mfem.Mesh(nx, ny, nz, "HEXAHEDRON", ...)

# From file:
mfem.Mesh("model.mesh")     # MFEM native
mfem.Mesh("model.vtk")
mfem.Mesh("model.msh")      # Gmsh
```

## Refining

```python
mesh.UniformRefinement()          # halves edge lengths
for _ in range(3):
    mesh.UniformRefinement()     # 4^3 = 64x more elements
```

## Higher-order elements

```python
fec = mfem.H1_FECollection(order=2, dim=dim)   # quadratic
fec = mfem.H1_FECollection(order=3, dim=dim)   # cubic
```

Higher order = fewer mesh cells needed for same accuracy.

## Coefficients

```python
one = mfem.ConstantCoefficient(1.0)

class MyCoeff(mfem.PyCoefficient):
    def EvalValue(self, x):
        return x[0] * x[1]        # variable coefficient f(x,y)=xy

f = MyCoeff()
b.AddDomainIntegrator(mfem.DomainLFIntegrator(f))
```

## Output

```python
# Save mesh + solution
mesh.Print("out.mesh")
x.Save("out.gf")

# Save as VTK for ParaView
mesh.PrintVTK(open("out.vtk", "w"))
x.SaveVTK(open("out.vtk", "a"), "Temperature", 1)
```

## Gotchas

- `ess_tdof_list` must be filled BEFORE `FormLinearSystem` — the BCs
  are applied during that call
- `FormLinearSystem` writes into output args (A, X, B) — they MUST be
  constructed (empty) MFEM objects before the call
- `x.Assign(value)` sets the Dirichlet boundary value (since the RHS
  absorbs the BC contribution); non-zero BCs go here
- `RecoverFEMSolution` is required after solve — otherwise `x` doesn't
  have the full solution (only interior DOFs)
