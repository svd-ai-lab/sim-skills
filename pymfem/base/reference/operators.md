# MFEM Bilinear/Linear Form Integrators

> Applies to: MFEM 4.8

## Bilinear form integrators (for a(u, v))

Common physics → integrator mapping:

| Physics | Integrator | Weak form | Typical FE |
|---------|-----------|-----------|-----------|
| -Δu + αu | `DiffusionIntegrator` + `MassIntegrator` | ∫∇u·∇v + α∫uv | H1 |
| Convection b·∇u | `ConvectionIntegrator` | ∫(b·∇u) v | H1 |
| Vector Laplacian (elasticity) | `ElasticityIntegrator(λ, μ)` | ∫σ(u):ε(v) | H1 vector |
| Mass (vector) | `VectorFEMassIntegrator` | ∫u·v | RT/ND |
| Div-div | `DivDivIntegrator` | ∫(∇·u)(∇·v) | RT |
| Curl-curl | `CurlCurlIntegrator` | ∫(∇×u)·(∇×v) | ND |
| Reaction | `MassIntegrator(c)` | ∫c u v | H1 / L2 |

Add to bilinear form:

```python
a = mfem.BilinearForm(fespace)
a.AddDomainIntegrator(mfem.DiffusionIntegrator(k_coeff))
a.AddDomainIntegrator(mfem.MassIntegrator(c_coeff))
a.Assemble()
```

## Linear form integrators (for b(v))

| Source | Integrator | Weak form |
|--------|-----------|-----------|
| Volume source f | `DomainLFIntegrator(f)` | ∫f v dx |
| Neumann flux g | `BoundaryLFIntegrator(g)` | ∫g v ds on Γ_N |
| Pressure load p·n | `VectorBoundaryLFIntegrator(p_vec)` | ∫p·n·v ds (elasticity) |

```python
b = mfem.LinearForm(fespace)
b.AddDomainIntegrator(mfem.DomainLFIntegrator(f_coeff))

neumann_bdr = mfem.intArray([0, 1, 0, 0])
b.AddBoundaryIntegrator(
    mfem.BoundaryLFIntegrator(g_coeff), neumann_bdr,
)
b.Assemble()
```

## Boundary integrators (mixed BCs, Robin)

```python
# Robin: α u + β ∂u/∂n = γ  → (α/β) contributes to bilinear, γ/β to linear
robin_bdr = mfem.intArray([1, 0, 1, 0])
a.AddBoundaryIntegrator(
    mfem.MassIntegrator(alpha_over_beta), robin_bdr,
)
b.AddBoundaryIntegrator(
    mfem.BoundaryLFIntegrator(gamma_over_beta), robin_bdr,
)
```

## Vector elasticity example

```python
E, nu = 1e9, 0.3
lam = mfem.ConstantCoefficient(E*nu / ((1+nu)*(1-2*nu)))
mu = mfem.ConstantCoefficient(E / (2*(1+nu)))

fespace = mfem.FiniteElementSpace(mesh, fec, dim=mesh.Dimension())
a = mfem.BilinearForm(fespace)
a.AddDomainIntegrator(mfem.ElasticityIntegrator(lam, mu))

# Traction on right boundary
traction = mfem.Vector([1.0, 0.0])
traction_coeff = mfem.VectorConstantCoefficient(traction)
b = mfem.LinearForm(fespace)
right_bdr = mfem.intArray([0, 1, 0, 0])
b.AddBoundaryIntegrator(
    mfem.VectorBoundaryLFIntegrator(traction_coeff), right_bdr,
)
```

## Coefficient types

```python
# Constant (scalar)
c = mfem.ConstantCoefficient(5.0)

# Constant (vector)
v = mfem.VectorConstantCoefficient(mfem.Vector([1, 0, 0]))

# Variable (scalar): subclass PyCoefficient
class XY(mfem.PyCoefficient):
    def EvalValue(self, x):
        return x[0] * x[1]

# Variable (vector): subclass VectorPyCoefficient with Eval override
class GradU(mfem.VectorPyCoefficient):
    def __init__(self, dim):
        mfem.VectorPyCoefficient.__init__(self, dim)
    def EvalValue(self, x):
        return [x[0], x[1]]
```

## Gotchas

- Integrator objects are owned by the form after `AddDomainIntegrator` —
  don't reuse across forms
- `intArray` for boundary attribute markers: length = `mesh.bdr_attributes.Max()`,
  1 = "this boundary is active for this integrator"
- Variable coefficients via `PyCoefficient` cross the Python/C++ boundary
  at every quadrature point — SLOW. Use `ConstantCoefficient` or
  precomputed `GridFunctionCoefficient` when possible.
