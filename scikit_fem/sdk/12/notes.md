# scikit-fem 12.x Notes

## Provenance

- Source: PyPI `scikit-fem` package
- Installed version: 12.0.1
- Install path: standard pip site-packages in sim's venv

## API stability

scikit-fem 12.x is the current stable line as of 2026-04. Core API
(Mesh classes, Basis, BilinearForm, asm, solve, condense) has been
stable since 8.x.

## Capabilities verified

| Feature | Status | Notes |
|---------|--------|-------|
| `MeshTri` + `ElementTriP1` | Verified | Poisson E2E |
| `BilinearForm` / `LinearForm` | Verified | |
| `asm` assembly | Verified | Sparse CSR returned |
| `condense` + `solve` | Verified | Dirichlet BCs |
| `refined(n)` | Verified | 4^4 = 256 triangles on unit square |
| `skfem.helpers.grad/dot` | Verified | Used in Poisson weak form |

## Optional dependencies

- `meshio` — read/write .msh, .vtk, .xdmf, ...
- `matplotlib` — visualization (skfem.visuals.matplotlib)
- `pyvista` — 3D rendering
- `pyamg` — algebraic multigrid preconditioner

Install as needed: `pip install scikit-fem[all]` bundles them.

## Version detection

Driver runs `python -c "import skfem; print(skfem.__version__)"` in
subprocess. Output for this build: `12.0.1`, normalized to short `12.0`.
