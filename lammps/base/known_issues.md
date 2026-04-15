# Known Issues — LAMMPS Driver

## pip `lammps` wheel requires OpenMPI

**Discovered**: 2026-04-14
**Status**: Use source build instead
**Description**: `pip install lammps` installs a wheel that dynamically
links `libmpi.so.12` (OpenMPI). Systems with only MPICH fail at import.
**Workaround**: Build from source (`make serial` in `lammps/src/`)
which produces a self-contained `lmp_serial` binary without MPI.

## Debian `calculix-ccx` style glibc mismatch

**Status**: Source build sidesteps this
**Description**: Pre-built `.deb` packages (both buster and bookworm)
require newer glibc than Debian 10 provides. Source build from
`stable_29Aug2024` compiles cleanly with the system gcc.

## No potentials installed by default

**Status**: User-input driven
**Description**: Source build without `make yes-<pkg>` only includes
core styles. Pair styles like `eam/alloy`, `tersoff`, `reaxff` require
their packages enabled at build time (`make yes-MANYBODY`, etc.).
Check `lmp -h` output for "Installed packages" list.

## Lost atoms = silent failure

**Status**: LAMMPS design
**Description**: If a simulation becomes unstable (bad potential, time
step too large, close overlapping atoms), atoms may fly out of the box.
Default behavior is FATAL error "Lost atoms", but `thermo_modify lost
ignore` silently discards them — leading to wrong results.
**Acceptance check**: final step count == requested run count.

## log.lammps thermo block has variable columns

**Status**: Handled in E2E script
**Description**: The thermo column list depends on `thermo_style`. Parse
dynamically: first find header row starting with "Step", then parse
subsequent data rows until "Loop time".
