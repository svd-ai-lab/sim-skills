# Known Issues — SU2 Driver

## Marker name mismatch is silent until solve

**Discovered**: generic SU2 issue
**Description**: If `.cfg` has `MARKER_EULER= ( lowerwall )` but the
mesh defines `MARKER_TAG= lower_wall`, SU2 logs a warning but proceeds
with misapplied BCs. Always verify marker names against the mesh before
running.
**Detection**:
```
grep MARKER_TAG mesh.su2 | sort -u
grep MARKER_ config.cfg
```

## Output file overwrite

**Status**: By design
**Description**: `restart_flow.dat`, `flow.vtu`, `history.csv` overwrite
in cwd. For parameter sweeps, use a fresh directory per run. The E2E
script uses `tempfile.TemporaryDirectory`.

## Serial binary vs MPI

**Discovered**: 2026-04-14
**Status**: Choose at install time
**Description**: The official v8.4 Linux release ships two zips:
`SU2-v8.4.0-linux64.zip` (serial) and `SU2-v8.4.0-linux64-mpi.zip`
(OpenMPI). We installed serial. For production runs > 10k cells, install
the MPI build and use `mpirun -n N SU2_CFD`.

## Screen output limits

**Status**: User-input driven
**Description**: Default `SCREEN_OUTPUT` is large. For capture in sim's
stdout log, trim to: `SCREEN_OUTPUT= ( INNER_ITER, RMS_DENSITY )`. Full
convergence is always in `history.csv`.

## CFL instability on coarse meshes

**Status**: Tuning issue
**Description**: CFL=10+ on a coarse mesh can diverge at startup. Start
low (CFL=4) and use `CFL_ADAPT= YES` to ramp.

## history.csv header whitespace

**Discovered**: 2026-04-14
**Status**: Handled in E2E script
**Description**: SU2 pads CSV headers: `"    rms[Rho]    "`. Always
`.strip().strip('"')` each column name before index lookup.
