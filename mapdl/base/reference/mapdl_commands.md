# MAPDL command conventions — Pythonic vs raw APDL

> Source: https://mapdl.docs.pyansys.com/version/stable/user_guide/mapdl.html
> Last verified: 2026-04-14

## Two ways to send the same command

```python
mapdl.k(1, 0, 0, 0)          # Pythonic wrapper (preferred)
mapdl.run("K, 1, 0, 0, 0")   # raw APDL string
```

The wrapper does automatic string formatting, type coercion, and
output parsing; the raw form is a last resort when PyMAPDL hasn't
wrapped a given command yet.

## Legal analysis workflow (Static Structural skeleton)

```python
from ansys.mapdl.core import launch_mapdl

mapdl = launch_mapdl()

# 1. Preprocessing
mapdl.prep7()
mapdl.et(1, "SOLID186")                 # element type
mapdl.mp("EX", 1, 210e9)                # Young's modulus, Pa
mapdl.mp("PRXY", 1, 0.3)                # Poisson ratio
mapdl.mp("DENS", 1, 7800)               # density, kg/m^3
mapdl.blc4(0, 0, 0.1, 0.01)             # geometry (area, 100x10 mm)
mapdl.vext("ALL", dz=0.005)             # extrude to volume
mapdl.esize(0.005)                       # global mesh size
mapdl.vmesh("ALL")                       # mesh all volumes
mapdl.nsel("S", "LOC", "X", 0)           # pick nodes at X=0
mapdl.d("ALL", "UX", 0)                  # fix X
mapdl.d("ALL", "UY", 0)
mapdl.d("ALL", "UZ", 0)
mapdl.nsel("S", "LOC", "X", 0.1)
mapdl.f("ALL", "FX", 1000)               # apply force
mapdl.allsel()
mapdl.finish()

# 2. Solve
mapdl.solution()                         # /SOLU
mapdl.antype("STATIC")
mapdl.solve()
mapdl.finish()

# 3. Post-processing
mapdl.post1()                            # /POST1
mapdl.set(1, 1)                          # load step 1, substep 1
ux = mapdl.post_processing.nodal_displacement("X")
```

**Rule**: every processor-switch verb (`prep7`, `solution`, `post1`)
should be paired with a later `finish()`; forgetting `finish()` means
some commands silently route to the wrong processor.

## Converting legacy APDL decks

If you have an existing `.dat` / `.mac` input file:

```python
# Option A: load the file verbatim
mapdl.input(r"legacy/static.dat")

# Option B: convert to PyMAPDL Python first (one-time)
from ansys.mapdl import core as pymapdl
pymapdl.convert_script("static.dat", "static.py", macros_as_functions=True)
```

Option A is idiomatic for "run an existing deck"; Option B is for
"port an existing deck forward" (manual cleanup usually required
afterwards).

## `non_interactive` context

APDL control flow (`*IF`, `*DO`, `*CREATE`) doesn't execute correctly
when sent command-by-command over gRPC — MAPDL doesn't know the
following lines belong to a block. The fix:

```python
with mapdl.non_interactive:
    mapdl.run("*DO,I,1,10")
    mapdl.n("I", "I*1.0", 0, 0)
    mapdl.run("*ENDDO")
```

PyMAPDL buffers everything inside the `with` block, writes it to a
temp file, and sends it to MAPDL via `mapdl.input()` as one batch.

**Rule**: never read state (`mapdl.parameters[...]`, `mapdl.mesh.nnum`)
inside a `non_interactive` block — the buffered commands haven't been
executed yet, so you'll see stale values.

## Common parameter access pattern

```python
# Set and read APDL scalar parameters
mapdl.run("ARG1 = 0.01")
v = mapdl.parameters["ARG1"]         # → 0.01 (float)

# Get from array:
mapdl.get("MAXSTRESS", "PLNSOL", 0, "MAX")
v = mapdl.parameters["MAXSTRESS"]
```

## Output parsing on list-style commands

PyMAPDL enriches return values from listing commands so they can be
consumed as numpy/pandas:

```python
cmd = mapdl.prnsol("U", "X")         # nodal displacements as string
arr = cmd.to_array()                   # numpy (N, 2): [node_id, UX]
df = cmd.to_dataframe()                # pandas

cmd = mapdl.nlist()
df = cmd.to_dataframe()                # node coords as DataFrame
```

Commands that support this: `prnsol`, `presol`, `prenergy`, `prrfor`,
`nlist`, `dlist`, `flist`, `elist`, `set("LIST")`.

## Gotchas

- **`ALLSEL()` discipline**: before `solve()` always call `mapdl.allsel()`.
  A dangling selection from a BC pick will cause the solve to see only
  a subset of the model.
- **Empty return values**: some commands return empty strings rather
  than raising on "no matches" (e.g. `nsel("S", "LOC", "X", 99e9)` on
  an empty selection). Check `len(mapdl.mesh.nnum)` after critical
  selections.
- **Units are NOT enforced**: MAPDL is unit-agnostic; mixing SI and
  imperial silently gives wrong answers. Always call `mapdl.units("SI")`
  (or your chosen system) once at the top of the script.
