# PyMAPDL SDK API — launch, connect, interact

> Source: https://mapdl.docs.pyansys.com/version/stable/getting_started/launcher.html
> SDK version: ansys-mapdl-core 0.68+
> Last verified: 2026-04-14

## Overview

PyMAPDL (`ansys-mapdl-core`) is a **gRPC client** for Ansys MAPDL. When
you call `launch_mapdl()` the SDK starts `ANSYS<ver>.exe -grpc` as a
subprocess (default port `50052`), then connects as a gRPC client. The
returned `Mapdl` object is a live handle — every method call becomes a
gRPC message to the solver.

Key consequence: the solver process outlives your Python script only if
you never call `mapdl.exit()`. If you want persistent sessions (sim's
`sim connect / exec / inspect`), hold the `Mapdl` object across calls
instead of re-launching.

## Launch

```python
from ansys.mapdl.core import launch_mapdl

# Simplest — auto-detect MAPDL via AWP_ROOT<ver> env var
mapdl = launch_mapdl()

# Pin a specific install
mapdl = launch_mapdl(
    exec_file=r"E:\Program Files\ANSYS Inc\v241\ansys\bin\winx64\ansys241.exe",
    run_location=r"C:\sim_work",   # where .rst, .db, etc. land
    nproc=4,                         # MPI ranks
    loglevel="ERROR",                # suppress warnings spam
)

# Connect to an already-running gRPC server (launched by someone else)
mapdl = launch_mapdl(start_instance=False, ip="127.0.0.1", port=50052)
```

**Install detection chain** (in order PyMAPDL checks):
1. `PYMAPDL_MAPDL_EXEC` env var → direct path
2. `AWP_ROOT<xxx>` env var → `<root>/ansys/bin/<os>/ansys<xxx>.exe`
3. Cached `~/.ansys/config.txt` from prior `change_default_ansys_path()`
4. Interactive prompt (blocking — avoid in server/agent contexts)

## Core API surface

```python
mapdl.prep7()              # /PREP7    — enter preprocessor
mapdl.solution()           # /SOLU     — enter solver
mapdl.post1()              # /POST1    — enter postprocessor
mapdl.finish()             # FINISH    — exit current processor

mapdl.et(1, "SOLID186")    # ET        — define element type
mapdl.mp("EX", 1, 210e9)   # MP        — material property
mapdl.k(1, 0, 0, 0)        # K         — keypoint
mapdl.n(1, 0, 0, 0)        # N         — node
mapdl.e(1, 2)              # E         — element from nodes
mapdl.d("ALL", "UX")       # D         — displacement BC
mapdl.f(3, "FZ", -1000)    # F         — nodal force
mapdl.solve()              # SOLVE     — run the analysis
mapdl.exit()               # terminate MAPDL + gRPC server
```

**Name mangling rule**: MAPDL commands starting with `/` or `*` get
renamed for Python safety:

| APDL | Python |
|---|---|
| `/PREP7` | `mapdl.prep7()` |
| `/SOLU` | `mapdl.solution()` |
| `/POST1` | `mapdl.post1()` |
| `*GET` | `mapdl.starstatus()` or `mapdl.get_value(...)` helper |
| `*IF` / `*DO` | Use Python `if` / `for`, or `with mapdl.non_interactive:` |

## Escape hatches

```python
mapdl.run("/PREP7")                 # raw APDL one-liner
mapdl.input("legacy_deck.dat")       # run an APDL input file
mapdl.input_strings("""...""")       # multi-line APDL block
with mapdl.non_interactive:          # buffer commands → one batch
    mapdl.k(1, 0, 0, 0)
    mapdl.k(2, 1, 0, 0)
```

## State introspection (without round-tripping to POST1)

```python
len(mapdl.mesh.nnum)        # node count
len(mapdl.mesh.enum)        # element count
mapdl.mesh.nodes            # (N, 3) numpy coords
mapdl.result                # lazy ResultFile reader — see postprocessing.md
mapdl.parameters["MYVAR"]   # MAPDL scalar parameter
mapdl.jobname               # current jobname
mapdl.directory             # working directory MAPDL sees
```

## Gotchas

- **Locale / license prompts**: first-ever launch may prompt for the
  MAPDL binary path and license — run `launch_mapdl()` once manually
  before wiring it into a non-interactive pipeline.
- **Port collisions**: default `50052`. If multiple MAPDL sessions must
  coexist, set `port=` explicitly per call; PyMAPDL will auto-pick a
  free port if you pass `port=0`.
- **Zombie servers**: if your script raises before `mapdl.exit()` the
  `ANSYS<ver>.exe` process keeps running. Wrap lifetime in
  `try/finally` or use `with launch_mapdl() as mapdl:`.
- **ansys-tools-path deprecation warning**: `find_mapdl()` prints a
  DeprecationWarning as of pymapdl 0.72 — this is noise, not a bug.
