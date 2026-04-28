# PyMFEM 4.8 Notes

## Provenance

- Source: PyPI `mfem` package
- Version: 4.8.0.1
- Contains compiled MFEM C++ library + Python bindings (SWIG)

## Capabilities verified on this build

| Feature | Status | Notes |
|---------|--------|-------|
| `mfem.Mesh` (2D triangular built-in) | Verified | 20×20 square |
| `H1_FECollection(1, dim)` | Verified | Linear nodal elements |
| `DiffusionIntegrator` + `DomainLFIntegrator` | Verified | Poisson weak form |
| `FormLinearSystem` + `RecoverFEMSolution` | Verified | BC application workflow |
| `UMFPackSolver` | Verified | Direct solve |
| `GridFunction.GetDataArray()` | Verified | Returns numpy array |

## Import pattern

Serial (our default):
```python
import mfem.ser as mfem
```

Parallel (requires separate `mfemp` install, NOT included in plain
`pip install mfem`):
```python
import mfem.par as mfem
from mpi4py import MPI
```

## Version detection

`python -c "import importlib.metadata as md; print(md.version('mfem'))"`
returns `4.8.0.1`. Normalized to short form `4.8`.
