---
name: hypermesh-sim
description: Use when pre-processing FE models via Altair HyperMesh -- CAD geometry import (STEP/IGES/CATIA/NX), surface and volume meshing (automesh/tetmesh/batchmesh), element quality checks (aspect/skew/jacobian), material/property/load assignment, and solver deck export (OptiStruct/Nastran/Abaqus/LS-DYNA/Radioss) through the hm Python API in batch mode.
---

# hypermesh-sim

You are connected to **HyperMesh** via sim-cli.

HyperMesh is Altair's high-performance FE pre-processor. It is sim's
**heavyweight meshing and model-building tool** for crash, NVH,
durability, and CFD pre-processing.

- Import CAD geometry (STEP, IGES, CATIA, NX, SolidWorks, Creo, JT, Parasolid)
- Surface mesh (automesh, batchmesh) and volume mesh (tetmesh)
- 225 entity classes (Node, Element, Material, Property, Component, etc.)
- 1946 model methods (meshing, quality checks, connectors, loads, export)
- Element quality checks (aspect ratio, skew, jacobian, warpage, etc.)
- Export to 20+ solver formats (OptiStruct, Nastran, Abaqus, LS-DYNA, Radioss)

Scripts use the `hm` Python API. Executed via
`sim run script.py --solver hypermesh` (one-shot batch via `hw -b -script`).

---

## Identity

| Field | Value |
|---|---|
| Solver | Altair HyperMesh (HyperWorks Desktop) |
| Execution mode | One-shot batch (`hw -b -script script.py`) |
| Session type | None (Phase 1) |
| SDK | `hm` Python API (bundled with HyperWorks Desktop) |
| Script language | Python |
| Input formats | `.hm`, `.hma`, STEP, IGES, CATIA, NX, SolidWorks, Creo, JT, Parasolid, Nastran, Abaqus, LS-DYNA |
| Output | JSON on stdout (last line), solver deck files (.fem/.bdf/.inp/.k/.rad) |

---

## Scope

**In scope:**
- CAD geometry import and cleanup
- Surface meshing (automesh, batchmesh) and volume meshing (tetmesh)
- Material, property, and component creation
- Load and constraint application
- Element quality checking and improvement
- Solver deck export (OptiStruct, Nastran, Abaqus, LS-DYNA, Radioss)
- Connector engineering (spot welds, seam welds, adhesives)

**Out of scope:**
- Solving (HyperMesh is pre-processing only -- use solver-specific skills)
- Post-processing (use HyperView, ParaView, or pyvista skills)
- Interactive GUI operations (batch mode only)
- Optimization setup (use HyperStudy)

---

## Hard constraints

1. **HyperMesh is NOT pip-installable.** Requires Altair HyperWorks Desktop
   installed with a valid license (Altair Units or node-locked).

2. **Scripts run inside HyperMesh's Python interpreter.** The `hm` module is
   only available within `hw -b -script` or the HyperMesh GUI console.
   Don't assume pip packages are available.

3. **Always start with `model = hm.Model()`.** Every script must create a Model
   instance as the entry point for all operations.

4. **Use Collections for entity selection, not IDs.** The Python API uses
   `hm.Collection(model, ent.EntityType)` instead of Tcl-style ID marks.
   Collections are persistent and composable.

5. **Never use InteractiveSelection in batch scripts.**
   `CollectionByInteractiveSelection`, `EntityByInteractiveSelection`, and
   `PlaneByInteractiveSelection` require GUI interaction and will fail in
   batch mode (`hw -b`).

6. **Check `hwReturnStatus.status` for errors.** All model methods return a
   status object. `status == 0` means success; non-zero means failure.
   The `.message` attribute contains details.

7. **Use `hm.setoption(block_redraw=1)` for batch performance.** Suppress
   GUI updates in batch scripts to avoid overhead. Also disable
   `command_file_state=0` and `entity_highlighting=0`.

8. **JSON result on last stdout line.** All snippets must
   `print(json.dumps({...}))` as the final output.

---

## File index

### base/ -- always relevant

| Path | Content |
|---|---|
| `base/reference/hm_api_overview.md` | Core `hm` API: Model, Session, Collection, entity classes |
| `base/reference/meshing.md` | Meshing operations: automesh, tetmesh, batchmesh, quality checks |
| `base/reference/entities_and_collections.md` | Entity manipulation patterns, FilterBy classes, CollectionSet |
| `base/reference/import_export.md` | CAD import, FE import/export, solver deck generation |
| `base/snippets/01_smoke_test.py` | Minimal: create model, material, property, report |
| `base/snippets/02_import_and_mesh.py` | Import geometry, automesh, count elements |
| `base/snippets/03_quality_check.py` | Element quality checks (aspect, skew, jacobian) |
| `base/snippets/04_export_deck.py` | Export solver deck (OptiStruct/Nastran) |
| `base/known_issues.md` | Discovered failure modes and workarounds |

### sdk/2025/ -- HyperWorks 2025 specifics

| Path | Content |
|---|---|
| `sdk/2025/notes.md` | Python API changes, new entity classes |

---

## Required protocol

### Step 0 -- Version check

```bash
sim check hypermesh
```

Confirm HyperMesh is installed and version is known.

### Step 1 -- Input validation (Category A/B/C)

| Input | Category | Action |
|---|---|---|
| CAD file path | A | Must be provided by user |
| Material properties (E, Nu, Rho) | A | Must ask -- do not guess |
| Element type (shell/solid) | A | Must ask |
| Mesh size | A | Must ask |
| Quality criteria | A | Must ask -- "jacobian > 0.3, aspect < 5" |
| Solver format | A | Must ask -- OptiStruct/Nastran/Abaqus/LS-DYNA |
| Element order (1st/2nd) | B | Default 1st order, disclose |
| Performance options (block_redraw) | B | Default on, disclose |

### Step 2 -- Import geometry

```python
model.readfile(filename="model.hm", load_cad_geometry_as_graphics=0)
# or for CAD:
model.geomimport(filename="part.step")
```

### Step 3 -- Create materials and properties

```python
mat = ent.Material(model)
mat.name = "Steel"
mat.cardimage = "MAT1"
mat.E = 2.1e5
mat.Nu = 0.3
```

### Step 4 -- Mesh and check quality

Generate mesh, run quality checks, report metrics.

### Step 5 -- Export and acceptance

Export solver deck. Validate against user-specified quality criteria.
`exit_code == 0` alone is NOT sufficient.
