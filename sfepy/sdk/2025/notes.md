# SfePy 2025.x Notes

## Provenance

- Source: PyPI `sfepy`
- Verified version: 2025.4
- Pure Python + NumPy/SciPy + Cython inner loops (bundled in wheel)

## Capabilities verified

| Feature | Status | Notes |
|---------|--------|-------|
| `gen_block_mesh` | Verified | 2D quad block |
| `FEDomain` + `create_region` | Verified | 'all' + 'vertices in ...' |
| `Field.from_args` | Verified | scalar P1 |
| `Term.new('dw_laplace', ...)` | Verified | Poisson weak form |
| `Term.new('dw_volume_lvf', ...)` | Verified | constant source |
| `EssentialBC` + `Conditions` | Verified | homogeneous Dirichlet |
| `Newton + ScipyDirect` | Verified | linear convergence in 1 iter |
| `state.get_state_parts()['u']` | Verified | result extraction |

## Poisson benchmark

8x8 quad mesh, P1, f=1, u=0 on boundary
→ u_max = 0.0746 (analytical 0.0737, 1.3% rel error).

## Version detection

```bash
python3 -c "import sfepy; print(sfepy.__version__)"
```
returns `2025.4`. Driver normalizes to short form `2025.4`.

## Scientific deps installed alongside

The wheel pulls in: numpy, scipy, sympy, meshio, pyvista, tables (HDF5),
imageio, pillow, rich. Install size ~200 MB.
