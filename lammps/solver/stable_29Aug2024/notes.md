# LAMMPS stable_29Aug2024 Notes

## Provenance

- Source: `git clone --branch stable_29Aug2024 https://github.com/lammps/lammps.git`
- Build: `cd src && make serial -j 4` (pure g++ / gfortran, no MPI)
- Install path: `/data/Chenyx/sim/opt/lammps/src/lmp_serial`

## Capabilities verified on this build

| Feature | Status | Notes |
|---------|--------|-------|
| Core styles | Verified | lj/cut, harmonic, etc. |
| `units lj` | Verified | LJ liquid E2E |
| NVT Nose-Hoover | Verified | `fix nvt temp` |
| FCC lattice init | Verified | `create_atoms` |
| thermo output | Verified | parsed in E2E |

## Limitations of serial build

- No MPI scaling (single rank only)
- No GPU support (no `pair_style lj/cut/gpu`)
- Excluded optional packages: KOKKOS, ML-IAP, REAXFF by default
- To enable a package: `cd src && make yes-<package> && make serial`

## Commonly enabled packages

```
make yes-MANYBODY        # eam, tersoff, sw
make yes-MOLECULE        # bond/angle/dihedral styles
make yes-KSPACE          # long-range Coulombics (Ewald/PPPM)
make yes-RIGID           # rigid body dynamics
make yes-REPLICA         # replica exchange
make serial              # rebuild
```

## Version detection

`lmp -h` banner starts with:
```
LAMMPS (29 Aug 2024)
```

Driver parses date via regex `LAMMPS\s*\(([^)]+)\)` and normalizes to
YYYYMMDD (`20240829`) for comparability.
