# Known Issues — Elmer FEM Driver

## No pre-built Linux binaries

**Discovered**: 2026-04-14
**Status**: Build from source
**Description**: ElmerCSC GitHub releases do NOT ship Linux binaries —
only Windows installers. On Linux, source build via CMake is required.
**Workaround**: `git clone --branch release-26.1 https://github.com/ElmerCSC/elmerfem && mkdir build && cmake -DCMAKE_INSTALL_PREFIX=... -DWITH_MPI=ON .. && make -j && make install`
Takes ~20-30 minutes on 4 cores.

## LD_LIBRARY_PATH required

**Status**: Handled by driver
**Description**: `ElmerSolver` dynamically links `libelmersolver.so`,
which lives at `<prefix>/lib/elmersolver/`. The driver sets
`LD_LIBRARY_PATH` automatically when running.

## Mesh directory, not mesh file

**Status**: By design, user-input driven
**Description**: Unlike most solvers, Elmer reads a mesh *directory* of
4 files (`mesh.header`, `mesh.nodes`, `mesh.elements`, `mesh.boundary`).
Referenced in SIF as `Mesh DB "." "<dirname>"` → reads `./<dirname>/mesh.*`.
Use ElmerGrid to generate from .grd or convert from Gmsh.

## Block `End` required

**Status**: Elmer parser quirk
**Description**: Every `Header`, `Simulation`, `Body`, `Material`, etc.
must end with `End` on its own line. Missing `End` causes cascading
parse errors at later blocks — hard to trace. Lint catches the most
common case (missing Simulation).

## Active Solvers list must match solver indices

**Status**: User-input driven
**Description**: `Active Solvers(2) = 1 3` in an Equation block refers
to `Solver 1` and `Solver 3` blocks. If an Equation lists an index
without a matching Solver block, the solver silently doesn't run.

## ElmerSolver -v has no version string in some builds

**Status**: Best-effort version detection
**Description**: `ElmerSolver -v` output varies by build. The driver's
regex tries multiple patterns; falls back to "unknown" if none match.
Version is shown in banner printed at every run start.
