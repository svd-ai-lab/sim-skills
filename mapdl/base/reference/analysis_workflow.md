# Standard analysis workflow skeletons

> Source: distilled from https://mapdl.docs.pyansys.com/version/stable/examples/gallery_examples/
> Last verified: 2026-04-14

MAPDL does not have "system templates" like Workbench does. Instead,
every analysis follows the same five-phase skeleton: **launch → prep7
→ solve → post1 → exit**. The differences between analysis types are
confined to the `antype(...)` call and the BCs / material choices.

## Static Structural (most common)

```python
from ansys.mapdl.core import launch_mapdl

mapdl = launch_mapdl(run_location=r"C:\sim_work")

# PREP7
mapdl.prep7()
mapdl.units("SI")
mapdl.et(1, "SOLID186")
mapdl.mp("EX", 1, 210e9); mapdl.mp("PRXY", 1, 0.3); mapdl.mp("DENS", 1, 7800)
# ... geometry, mesh, BCs ...
mapdl.finish()

# SOLU
mapdl.slashsolu()              # alias for .solution() / /SOLU
mapdl.antype("STATIC")          # the analysis-type switch
mapdl.solve()
mapdl.finish()

# POST1
mapdl.post1()
mapdl.set(1, 1)
ux = mapdl.post_processing.nodal_displacement("X")
seqv = mapdl.post_processing.nodal_eqv_stress()

mapdl.exit()
```

## Modal (natural frequencies)

```python
mapdl.slashsolu()
mapdl.antype("MODAL")
mapdl.modopt("LANB", nmode=10)           # 10 modes, Block-Lanczos
mapdl.mxpand(10)                          # expand all 10 mode shapes
mapdl.solve()
mapdl.finish()

mapdl.post1()
for i in range(1, 11):
    freq = mapdl.get("freq_%d" % i, "MODE", i, "FREQ")
    print(i, mapdl.parameters["freq_%d" % i])
```

## Transient Thermal

```python
mapdl.prep7()
mapdl.et(1, "SOLID70")
mapdl.mp("KXX", 1, 60.5)     # conductivity W/m-K
mapdl.mp("C", 1, 434)         # specific heat J/kg-K
mapdl.mp("DENS", 1, 7850)
# ... geometry + mesh ...
mapdl.finish()

mapdl.slashsolu()
mapdl.antype("TRANS")
mapdl.trnopt("FULL")
mapdl.tref(20)                # reference temp C
mapdl.time(10.0)               # end time
mapdl.deltim(0.1)              # Δt
mapdl.solve()
mapdl.finish()

mapdl.post26()                  # note: post26 for time-history, not post1
# Or loop through substeps:
mapdl.post1()
for s in range(1, 101):
    mapdl.set(1, s)
    t = mapdl.post_processing.nodal_temperature()
```

## Harmonic Response

```python
mapdl.slashsolu()
mapdl.antype("HARMIC")
mapdl.harfrq(0, 500)           # sweep 0–500 Hz
mapdl.nsubst(100)
mapdl.kbc(1)                    # stepped loading
mapdl.solve()
```

## Common element types (pick from EXAMPLES/*)

| Physics | Element | Notes |
|---|---|---|
| 1D beams | `BEAM188` / `BEAM189` | Slender members; `sectype` for cross-sections |
| 2D plane stress | `PLANE183` | Needs `KEYOPT(3)=3` + thickness |
| 3D solid | `SOLID186` (20-node) / `SOLID185` (8-node) | Default structural choice |
| 3D thermal | `SOLID70` / `SOLID90` | Heat conduction |
| Surface contact | `CONTA174` + `TARGE170` | Auto-generate with `mapdl.cnto`, `mapdl.esurf` |
| Acoustic | `FLUID30` / `FLUID130` | Acoustic cavity + infinite domain |
| Magnetostatic | `PLANE53` / `SOLID96` | Low-frequency EM |

## Verification Manual (VM) files — vendor gold standard

Bundled with PyMAPDL:

```python
from ansys.mapdl.core import examples

mapdl.input(examples.vmfiles["vm10"])    # simple cantilever — Tier A example
mapdl.solve()
```

Available VM files (partial list):
- `vm1` — Statically indeterminate reaction force
- `vm10` — Bending of a T-section beam
- `vm37` — Elongation of a solid bar
- `vm100` — Harmonic response of a beam

These are the **gold-standard Tier A examples** per the skill-create
methodology (vendor-validated with published reference numbers).

## Troubleshooting tree

| Symptom | Likely cause | Fix |
|---|---|---|
| `MapdlRuntimeError` on basic command | Wrong processor | Call the matching `prep7()`/`slashsolu()`/`post1()` first |
| All-zero displacement/stress | Missing `set(1, 1)` in POST1 | Add `mapdl.set(1, 1)` before querying |
| "No solution available" | Selection wrong at solve time | Call `mapdl.allsel()` before `solve()` |
| Mesh won't generate | No element type defined | `mapdl.et(1, "SOLID186")` before `vmesh` |
| Hang on launch | License server unreachable | Check `ANSYSLMD_LICENSE_FILE` |
| Units nonsense | Mixed unit systems | Call `mapdl.units("SI")` once at top |
