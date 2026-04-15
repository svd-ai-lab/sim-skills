# MAPDL postprocessing — data + visualization

> Source: https://mapdl.docs.pyansys.com/version/stable/user_guide/post.html
> Last verified: 2026-04-14

## Three ways to get results out of MAPDL

| Path | Use when | Returns |
|---|---|---|
| `mapdl.post_processing.*` | You have a live `Mapdl` session | numpy arrays + PyVista plots |
| `mapdl.result.*` (ansys-mapdl-reader) | You want to inspect a `.rst` file after the fact | numpy arrays + PyVista plots |
| DPF (`ansys-dpf-core`) | Modern, headless, works with `.rst`/`.rth`/`.rfrq` | DPF fields |

Phase 1 of this skill targets the **first path** — live `Mapdl`
session via PyMAPDL — because it's the simplest end-to-end.

## Live-session post-processing

After `mapdl.solve()` + `mapdl.post1()`:

```python
mapdl.post1()
mapdl.set(1, 1)                                    # load step 1, substep 1

# Scalar aggregates
ux = mapdl.post_processing.nodal_displacement("X")            # (N,)
uy = mapdl.post_processing.nodal_displacement("Y")
uz = mapdl.post_processing.nodal_displacement("Z")
umag = mapdl.post_processing.nodal_displacement("NORM")       # magnitude
seqv = mapdl.post_processing.nodal_eqv_stress()               # von Mises
reac = mapdl.post_processing.nodal_reaction_forces("FX")

# Data accessors
print(ux.max(), ux.min(), ux.mean())
```

## Headless plotting (saves PNG — no display required)

```python
# Single-click: render to PNG without opening a window
mapdl.post_processing.plot_nodal_displacement(
    "NORM",
    savefig="disp_norm.png",
    off_screen=True,
    window_size=(1200, 800),
    cmap="viridis",
    show_edges=True,
)

# Same for stress
mapdl.post_processing.plot_nodal_eqv_stress(
    savefig="seqv.png", off_screen=True
)

# Geometry and mesh plots (before solve) also support savefig
mapdl.eplot(savefig="mesh.png", off_screen=True)
mapdl.nplot(savefig="nodes.png", off_screen=True, nnum=True)
mapdl.vplot(savefig="volumes.png", off_screen=True, show_edges=True)
```

This satisfies the driver-development guide's **Step 8.5 "headless
first"** rule without any extra infrastructure — PyMAPDL's PyVista
integration is off-screen capable by design.

## Result-file reader (no live session)

When the `Mapdl` object is gone but the `.rst` file is on disk:

```python
from ansys.mapdl.reader import read_binary
rst = read_binary(r"C:\sim_work\file.rst")

nnum, disp = rst.nodal_solution(0)               # step 0 displacements
nnum, stress = rst.principal_nodal_stress(0)     # step 0 stresses
seqv = stress[:, -1]                              # von Mises column
max_stress = np.nanmax(seqv)

rst.plot_nodal_solution(0, "X", savefig="rst_ux.png", off_screen=True)
```

`read_binary` works for the `.rst` produced by any MAPDL version from
v15+ — useful for diffing runs, regression tests, and CI pipelines.

## Enriched listing output

The `PRNSOL` / `PRESOL` family of commands return strings with extra
methods attached:

```python
cmd = mapdl.prnsol("U", "X")
cmd.to_list()           # [[node_id, ux], ...]
cmd.to_array()          # numpy (N, 2)
cmd.to_dataframe()      # pandas
```

Available on: `prnsol`, `presol`, `prvect`, `prenergy`, `prrsol`,
`prjsol`, `prnld`, `prrfor`, `nlist`, `dlist`, `flist`, `elist`,
`prcint`, `prerr`, `priter`, `prpath`, `prsect`.

## Far-field / stress concentration pattern

Useful for verification benchmarks (see `3d_notch.md` example):

```python
# After solve
result = mapdl.result
nnum, stress = result.principal_nodal_stress(0)
von_mises = stress[:, -1]

# Far-field = nodes at the right edge of the plate (x = length)
mask = result.mesh.nodes[:, 0] == LENGTH
far_field = np.nanmean(von_mises[mask])

# Peak stress at the notch
peak = np.nanmax(von_mises)

stress_concentration = peak / far_field
```

## Gotchas

- **`set(1, 1)` is mandatory**: in POST1 you must load a specific
  substep before querying results. Skipping it raises silently with
  zero-filled arrays.
- **Mid-side nodes have no stress**: element-stress fields return NaN
  at quadratic mid-side nodes. Always use `np.nanmax` / `np.nanmean`
  for aggregates.
- **`off_screen=True` + CI**: on Linux CI without a display, also set
  `PYVISTA_OFF_SCREEN=true` and install `xvfb` to cover edge cases
  where pyvista still tries to open a GL context.
- **File-reader vs live session**: `mapdl.result.plot_*` and
  `mapdl.post_processing.plot_*` have nearly-identical signatures but
  come from **different libraries**. The live-session version is
  richer (knows current selection); the file-reader version is simpler.
