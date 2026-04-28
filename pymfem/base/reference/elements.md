# MFEM Finite Element Spaces

> Applies to: MFEM 4.8

## Element families

MFEM supports the full de Rham complex:
```
H1  ----grad----> H(curl) ----curl----> H(div) ----div----> L2
scalar            vector                vector              scalar
(nodal)           (edge)                (face)              (cell)
```

| FECollection | Continuity | Typical use |
|--------------|-----------|-------------|
| `H1_FECollection` | C⁰ continuous scalars | Heat, Poisson, elasticity (per component) |
| `ND_FECollection` | Tangentially continuous vectors (edges) | Maxwell E field |
| `RT_FECollection` | Normally continuous vectors (faces) | Maxwell B field, Darcy flux |
| `L2_FECollection` | Discontinuous | DG, pressure in Stokes |
| `DG_FECollection` | Discontinuous (synonym) | Hybridizable methods |

## Creating FE spaces

```python
import mfem.ser as mfem

fec_h1 = mfem.H1_FECollection(order=1, dim=2)
fec_h1_quadratic = mfem.H1_FECollection(order=2, dim=2)
fec_rt = mfem.RT_FECollection(order=0, dim=2)
fec_nd = mfem.ND_FECollection(order=0, dim=3)

# Scalar field
fespace = mfem.FiniteElementSpace(mesh, fec_h1)

# Vector-valued field (same FE per component)
fespace_vec = mfem.FiniteElementSpace(mesh, fec_h1, mesh.Dimension())

# Mixed: vector RT + scalar L2 (Darcy)
rt_space = mfem.FiniteElementSpace(mesh, fec_rt)
l2_space = mfem.FiniteElementSpace(mesh, fec_l2)
```

## DOF count

```python
print("Global DOFs:", fespace.GetTrueVSize())
print("Vdim:", fespace.GetVDim())            # components (1 for scalar)
```

## Element orders (higher-order)

| Order | Triangle DOFs/elem | Tet DOFs/elem | Quad DOFs/elem |
|-------|--------------------|--------------:|----------------|
| 1 (linear) | 3 (vertices) | 4 | 4 |
| 2 (quadratic) | 6 | 10 | 9 |
| 3 (cubic) | 10 | 20 | 16 |
| p (general) | (p+1)(p+2)/2 | (p+1)(p+2)(p+3)/6 | (p+1)² |

Higher order = higher accuracy per DOF, but stiffer matrix.

## hp-refinement

Non-conforming refinement (hanging nodes supported):

```python
elements_to_refine = mfem.intArray([0, 5, 9])
mesh.GeneralRefinement(elements_to_refine)
fespace.Update()
x.Update()
```

## Time-dependent spaces (unchanged)

For transient problems, the FE space is usually fixed across time steps
— only the GridFunction updates.

## Gotchas

- `H1_FECollection(p, dim)` — `p` is polynomial ORDER, not degrees of
  freedom
- For vector fields in `H1_FECollection`, use `FiniteElementSpace(mesh,
  fec, dim)` (4th arg = vector dimension) — not a separate vector FEC
- `ND` (edge elements) require `fec.CreateDOFElementMap` in some
  workflows — rarely exposed directly in PyMFEM
- DG spaces (`L2_FECollection`) need special integrators
  (InteriorFaceIntegrator, BdrFaceIntegrator) — not standard DomainIntegrator
