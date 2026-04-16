# ICEM CFD Tcl Scripting API

> Source: ICEM CFD 24.1 Programmer's Guide + install-bundled help
> Last verified: 2026-04-16

## Overview

ICEM CFD is scripted via Tcl 8.3.3 with a proprietary `ic_*` command
namespace. The batch runner is `med_batch.exe -script <file.tcl>` (or
`icemcfd.bat -batch -script <file.tcl>` which sets up PATH first).

There is **no Python SDK**. The only Python access is the
`IcemHexaBlocking` COM object via IronPython, limited to hex blocking
operations.

## Execution modes

| Mode | Command | Notes |
|---|---|---|
| GUI | `icemcfd.bat` or `med.exe` | Interactive, full UI |
| Batch | `icemcfd.bat -batch -script <file.tcl>` | Headless, best for `sim run` |
| Replay | `icemcfd.bat -script <file.rpl>` | Plays back recorded actions |

## Core ic_* command families

### Geometry (`ic_geo_*`)
```tcl
ic_geo_new_family "INLET"                    ;# create geometry family/part
ic_geo_create_point {0.0 0.0 0.0}            ;# create a point
ic_geo_create_curve_from_points {p1 p2 p3}   ;# curve through points
ic_geo_create_surface_from_curves {c1 c2}    ;# surface from curves
ic_geo_import_stl "model.stl"                ;# import STL geometry
```

### Unstructured meshing (`ic_uns_*`)
```tcl
ic_uns_set_mesh_params -global_size 0.1      ;# global mesh size
ic_uns_set_mesh_params -face_mesh tetra       ;# tetra volume mesh
ic_uns_run_mesh                               ;# generate mesh
ic_uns_get_mesh_stats                         ;# return node/element counts
```

### Hex blocking (`ic_hex_*` / `ic_blk_*`)
```tcl
ic_hex_create_block {-1 -1 -1} {1 1 1}      ;# bounding-box block
ic_hex_split_block x 0.5                     ;# split at x=0.5
ic_hex_set_mesh_params -edge_size 0.05       ;# edge mesh size
ic_hex_compute_mesh                           ;# generate hex mesh
```

### Boundary conditions (`ic_boco_*`)
```tcl
ic_boco_load "project.fbc"                   ;# load BC file
ic_boco_set_part "INLET" "Velocity Inlet"    ;# assign BC type
ic_boco_save "project.fbc"                   ;# save BC file
```

### File IO
```tcl
ic_load_tetin "geometry.tin"                 ;# load native geometry
ic_save_tetin "geometry.tin"                 ;# save native geometry
ic_save_mesh "output.msh" fluent             ;# export to Fluent format
ic_save_mesh "output.cfx" cfx               ;# export to CFX format
ic_save_mesh "output.inp" ansys              ;# export to ANSYS APDL
```

### Utility
```tcl
ic_batch_mode 1                              ;# force batch mode
ic_set_meshing_params global 0.1 ...         ;# set global meshing params
puts "done"                                  ;# Tcl standard output
exit 0                                       ;# clean exit from batch
```

## Typical batch workflow

```tcl
# 1. Load geometry
ic_load_tetin "model.tin"

# 2. Set meshing parameters
ic_uns_set_mesh_params -global_size 0.05
ic_uns_set_mesh_params -face_mesh tetra

# 3. Generate mesh
ic_uns_run_mesh

# 4. Check quality
set stats [ic_uns_get_mesh_stats]
puts "Mesh: $stats"

# 5. Export to Fluent
ic_save_mesh "output.msh" fluent

puts "Export complete"
exit 0
```

## 143 output interfaces

ICEM ships `.tcl` export modules for 143 solver formats in:
```
<ICEMCFD_ROOT>/win64_amd/icemcfd/output-interfaces/
```

Major ones: `fluent.tcl`, `cfx-5.tcl`, `ansys.tcl`, `abaqus.tcl`,
`lsdyna3d.tcl`, `nastran.tcl`, `openfoam.tcl`.

## File formats

| Format | Extension | Purpose |
|---|---|---|
| Tetin | `.tin` | Native geometry (points, curves, surfaces) |
| Project | `.prj` | Project file (references all components) |
| Blocking | `.blk` | Hex blocking definition |
| Unstructured | `.uns` | Unstructured domain mesh |
| BC family | `.fbc` | Boundary condition family file |
| Topology | `.top` | Block topology / connectivity |

## Gotchas

- **Tcl 8.3.3** — old; no `{*}` expansion, no `lmap`, limited `lsort`.
  Stay with classic Tcl patterns.
- **No error propagation by default**: `ic_*` commands print errors to
  stderr but return empty string. Wrap critical calls in `if {[catch
  {ic_uns_run_mesh} err]} { puts "ERROR: $err"; exit 1 }`.
- **Geometry must be closed**: surfaces must form a watertight volume
  for tetra meshing. Open surfaces → `ic_uns_run_mesh` silently
  produces zero elements.
- **Path separators**: use forward slashes even on Windows
  (`C:/simwork/model.tin`), or Tcl escaping (`C:\\simwork\\model.tin`).
- **Batch mode doesn't load GUI libraries**: commands that require
  display (e.g. `ic_display_*`) will fail silently.
