# ANSA Official Python API Documentation

Extracted from `E:\Program Files (x86)\ANSA\ansa_v25.0.0\docs\extending\python_api\`.

## Getting Started

| File | Source | Content |
|------|--------|---------|
| [getting_started_10minutes.md](getting_started_10minutes.md) | `getting_started/10minutes.html` | Script Editor, modules, Entity class, CollectEntities, CreateEntity, containers, complete example |
| [getting_started_intro.md](getting_started_intro.md) | `getting_started/intro_py.html` | Python primer: types, loops, functions, exceptions, OOP |
| [getting_started_interpreter.md](getting_started_interpreter.md) | `getting_started/interpreter.html` | Standalone Python 3.11.9 interpreter paths |
| [getting_started_script_editor.md](getting_started_script_editor.md) | `getting_started/script_editor.html` | Script Editor UI, debug mode, BCGui Designer |

## User Guide

| File | Source | Content |
|------|--------|---------|
| [user_guide_ansa_api_intro.md](user_guide_ansa_api_intro.md) | `user_guide/api_ansa/intro_ansa.html` | **Most important**: all 17+ modules, Entity class, deck constants, entity types, CollectEntities patterns, CreateEntity, GetEntityCardValues |
| [user_guide_remote_control.md](user_guide_remote_control.md) | `user_guide/remote_control/listener_mode.html` | IAP listener mode: launch, connect, hello/goodbye, run_script_text/file |

## API Reference

| File | Source | Content |
|------|--------|---------|
| [reference_mesh_api.md](reference_mesh_api.md) | `reference/api_ref_ansa/generated/ansa.mesh.html` | **356 functions**: surface/volume meshing, quality repair, hexa blocking, size fields |
| [reference_batchmesh_api.md](reference_batchmesh_api.md) | `reference/api_ref_ansa/generated/ansa.batchmesh.html` | 43 functions: scenarios, sessions, filters, parameters, execution |
| [reference_cad_api.md](reference_cad_api.md) | `reference/api_ref_ansa/generated/ansa.cad.html` | 13 functions: CAD translator internals (geometry queries, thickness) |

## Key Mesh Generation Functions

From `reference_mesh_api.md`:

```python
# Universal mesh generation (accepts FACE list or "visible")
mesh.Mesh(entities)

# Specific generators (operate on current selection/visible)
mesh.CreateFreeMesh()
mesh.CreateMapMesh()
mesh.CreateBestMesh()
mesh.CreateCfdMesh()

# Volume meshing
mesh.TetraFEM(entities, ...)
mesh.VolumesMeshV(volumes, mesh_type)

# Batch generator
mesh.BatchGenerator(entities)

# Quality repair
mesh.FixQuality()
mesh.ReconstructViolatingShells(expand_level)
mesh.Remesh()
```

## Key for sim Driver

- `drive_ansa.py` pattern → already implemented in `runtime.py`
- `listener_mode.html` → confirms our IAP implementation is correct
- `mesh.Mesh(faces)` → the correct API for geometry-to-mesh (needs FACE entities)
- `mesh.BatchGenerator(entities)` → alternative bulk mesh generation
- CAD import is via `base.Open()` (auto-detects format) — no separate InputIGES/InputSTL function
