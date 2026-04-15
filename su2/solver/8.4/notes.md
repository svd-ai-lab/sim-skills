# SU2 v8.4.0 "Harrier" Notes

## Provenance

- Source: GitHub Releases — https://github.com/su2code/SU2/releases/tag/v8.4.0
- Asset: `SU2-v8.4.0-linux64.zip` (serial, ~30 MB zipped, ~120 MB extracted)
- Install path: `/data/Chenyx/sim/opt/su2/bin/SU2_CFD`
- Alternative asset: `SU2-v8.4.0-linux64-mpi.zip` (not installed)

## Binaries shipped

| Binary | Purpose |
|--------|---------|
| `SU2_CFD` | Main flow/adjoint solver |
| `SU2_DEF` | Mesh deformation |
| `SU2_DOT` | Gradient projection (adjoint post) |
| `SU2_GEO` | Geometry preprocessing |
| `SU2_SOL` | Output (VTU) from restart file |
| `SU2_CFD_AD` | Algorithmic-differentiation-enabled solver (if built) |
| `SU2_Nastran` | Nastran → SU2 mesh converter |

Plus Python orchestration scripts:
- `parallel_computation.py`
- `shape_optimization.py`
- `compute_polar.py`
- ... more under `FADO/` and `FSI_tools/`

## Capabilities verified on this build

| Feature | Status | Notes |
|---------|--------|-------|
| Euler compressible | Verified | Inviscid Bump E2E (100 iter → RMS[Rho]=-4.91) |
| `.su2` mesh reading | Verified | 256×128 structured mesh |
| history.csv output | Verified | Parsed in E2E |
| VTU output | Verified | flow.vtu + surface_flow.vtu produced |
| Restart write | Verified | restart_flow.dat |

## Version detection

Driver parses output of `SU2_CFD --help`:
```
SU2 v8.4.0 "Harrier", The Open-Source CFD Code
```
Regex `SU2\s+v?(\d+\.\d+\.\d+)` → "8.4.0" → short "8.4".

## Limitations of serial build

- No MPI: `mpirun -n N SU2_CFD` won't scale past 1 rank
- OpenMP thread parallelism still works via `-t N` flag
- For large cases (> 100k cells), switch to the MPI zip
