# ICEM CFD meshing workflow patterns

> Source: distilled from ICEM help + output-interface Tcl modules
> Last verified: 2026-04-16

## Two meshing paradigms

| Paradigm | Tool | When to use |
|---|---|---|
| **Unstructured tetra** | `ic_uns_*` commands | Quick meshing, complex geometry, CFD general-purpose |
| **Structured hex (blocking)** | `ic_hex_*` / `ic_blk_*` commands | Turbomachinery, boundary layers, high-quality CFD |

## Unstructured tetra workflow

```tcl
# 1. Load watertight geometry
ic_load_tetin "model.tin"

# 2. Configure meshing
ic_uns_set_mesh_params -global_size 0.1
ic_uns_set_mesh_params -face_mesh tetra
# Optional: local refinement
ic_uns_set_mesh_params -part "INLET" -size 0.02

# 3. Generate
ic_uns_run_mesh

# 4. Quality check
set stats [ic_uns_get_mesh_stats]
puts "Stats: $stats"

# 5. Export
ic_save_mesh "output.msh" fluent
```

## Structured hex (blocking) workflow

```tcl
# 1. Load geometry
ic_load_tetin "model.tin"

# 2. Create blocking topology
ic_hex_create_block {-1 -1 -1} {1 1 1}
# Associate vertices to geometry points
ic_hex_set_vertex 1 {0 0 0}

# 3. Split & refine
ic_hex_split_block x 0.5
ic_hex_split_block y 0.3

# 4. Edge mesh sizing
ic_hex_set_mesh_params -edge_size 0.05
ic_hex_set_mesh_params -bunching_law biexponential

# 5. Compute
ic_hex_compute_mesh

# 6. Export
ic_save_mesh "output.msh" fluent
```

## Geometry import options

| Source | Tcl command |
|---|---|
| Native `.tin` | `ic_load_tetin "model.tin"` |
| STL | `ic_geo_import_stl "model.stl"` |
| STEP (via CAD reader) | Requires GUI or IGES fallback |
| IGES | `ic_geo_import_iges "model.igs"` |
| Parasolid | via `gemstotin.exe` converter |

## Meshing quality metrics

ICEM computes quality histograms automatically. Key metrics:
- **Determinant 2x2x2** (hex): > 0.3 is good, > 0.5 is excellent
- **Aspect ratio** (all): < 10 is good
- **Skewness** (all): < 0.9 is acceptable, < 0.7 is good
- **Minimum angle** (all): > 18° for tetra, > 36° for hex

## Batch-mode caveats

1. **Always `exit 0` at the end** — `med_batch.exe` hangs waiting for
   input otherwise.
2. **Geometry must be watertight** for tetra meshing — open surfaces
   produce zero-element meshes with no error.
3. **File paths**: use forward slashes on Windows (`C:/work/model.tin`)
4. **No display commands**: `ic_display_*`, `ic_view_*` etc. require
   a GUI and will fail silently in batch.
5. **`ic_batch_mode 1`** should be set early in the script to suppress
   interactive prompts from output interfaces.
