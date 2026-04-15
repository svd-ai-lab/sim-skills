# Elmer FEM 26.1 Notes

## Provenance

- Source: `git clone --branch release-26.1 https://github.com/ElmerCSC/elmerfem`
- Build: CMake with `WITH_MPI=ON`, `WITH_ELMERGUI=OFF`, `WITH_ElmerIce=OFF`
- Install: `/data/Chenyx/sim/opt/elmer/`
- Dependencies: gcc, gfortran, OpenMPI, BLAS/LAPACK (system)

## Binaries shipped

| Binary | Purpose |
|--------|---------|
| `ElmerSolver` | Main solver binary |
| `ElmerGrid` | Mesh generation + conversion |
| `ElmerSolver_mpi` | MPI-parallel solver (if built) |
| `Mesh2D` | Legacy 2D mesh generator |

## Dependencies at runtime

- `libelmersolver.so` (in `<prefix>/lib/elmersolver/`)
- `libmatc.so`
- OpenMPI runtime libs (system `/usr/lib/x86_64-linux-gnu/openmpi`)

Driver automatically sets `LD_LIBRARY_PATH` to include
`<prefix>/lib/elmersolver`.

## Capabilities verified (26.1 build)

| Feature | Status | Notes |
|---------|--------|-------|
| HeatSolve | Expected | Standard library shipped |
| StressSolve | Expected | Standard library shipped |
| ElmerGrid native `.grd` → mesh | Expected | Tested with unit square |
| SaveScalars | Expected | For programmatic result extraction |

## Not enabled in this build

- ElmerGUI (WITH_ELMERGUI=OFF) — graphical case builder
- ElmerIce (WITH_ElmerIce=OFF) — glaciology extensions
- External libraries (SUITESPARSE, MUMPS, HYPRE) — would need separate installs
