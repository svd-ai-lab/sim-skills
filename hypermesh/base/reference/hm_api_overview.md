# HyperMesh Python API Overview

> Applies to: HyperWorks Desktop 2024+
> Source: https://help.altair.com/hwdesktop/pythonapi/hypermesh/

## Module structure

```python
import hm                    # Core: Model, Session, Collection, filters, options
import hm.entities as ent    # 225 entity classes (Node, Element, Material, etc.)
```

## Model class

The entry point for all HyperMesh operations.

```python
model = hm.Model()           # Link to active model
model = hm.Model("mymodel")  # Link to named model
```

All 1946 HyperMesh commands are methods on the Model class:
```python
status = model.automesh(...)          # Returns hwReturnStatus
status = model.tetmesh(...)
status = model.feoutputwithdata(...)
```

### Key Model methods

| Method | Purpose |
|--------|---------|
| `model.readfile(filename, ...)` | Load .hm model file |
| `model.deletemodel()` | Clear current model |
| `model.geomimport(...)` | Import CAD geometry |
| `model.automesh(...)` | Surface automesh |
| `model.tetmesh(...)` | Volume tet mesh |
| `model.batchmesh2(...)` | Batch meshing |
| `model.feoutputwithdata(...)` | Export solver deck |
| `model.elementtestaspect(...)` | Aspect ratio check |
| `model.elementtestjacobian(...)` | Jacobian check |
| `model.hm_getmass(...)` | Query mass |
| `model.delete(entity)` | Delete an entity |
| `model.get(ent.Type, expr)` | Find single entity |

## Session class

Manages multiple models in one HyperMesh instance.

```python
session = hm.Session()
models = session.get_all_models()     # List of model names
current = session.get_current_model() # Active model name
exists = session.model_exists("name") # Check if model exists
```

## Return types

### hwReturnStatus (all modify functions)
```python
status = model.automesh(...)
if status.status == 0:
    print(f"Success: {status.message}")
else:
    print(f"Error: {status.message}")
```

### HmQueryResult (query functions)
```python
status, result = model.hm_getmass(collection=elems)
print(result.total_mass)
print(result.keys)  # List of available attributes
```

## Entity classes (hm.entities)

225 entity types. Common ones:

| Class | Usage |
|-------|-------|
| `ent.Node` | Mesh nodes |
| `ent.Element` | Mesh elements |
| `ent.Material` | Material definitions |
| `ent.Property` | Element properties (PSHELL, PSOLID, etc.) |
| `ent.Component` | Model components (mesh containers) |
| `ent.Surface` | CAD surfaces |
| `ent.Solid` | CAD solids |
| `ent.Line` | CAD lines/curves |
| `ent.Point` | CAD points |
| `ent.LoadForce` | Force loads |
| `ent.LoadConstraint` | SPC constraints |
| `ent.LoadPressure` | Pressure loads |
| `ent.Loadstep` | Load step definition |
| `ent.System` | Coordinate systems |
| `ent.Connector` | Weld/adhesive connectors |
| `ent.Part` | Assembly parts |
| `ent.Assembly` | Assembly groups |

### Create vs access existing

```python
# Create new entity (auto ID)
mat = ent.Material(model)
mat.name = "Steel"
mat.cardimage = "MAT1"
mat.E = 2.1e5

# Access existing entity by ID
mat5 = ent.Material(model, 5)
print(mat5.name)

# Set attributes
prop = ent.Property(model)
prop.cardimage = "PSHELL"
prop.materialid = mat       # Assign material
prop.PSHELL_T = 2.0         # Shell thickness
```

## Options

```python
# Performance optimization for batch
hm.setoption(
    block_redraw=1,           # Disable graphics refresh
    command_file_state=0,     # Disable command file
    entity_highlighting=0,    # Disable highlighting
    element_order=2,          # Second-order elements
    element_size=5.0,         # Default element size
    cleanup_tolerance=0.1,    # Geometry cleanup tolerance
)

# CAD reader options
hm.setoption_cadreader("step", "TargetUnits", "MMKS (mm kg N s)")
```

## Batch script template

```python
import json
import hm
import hm.entities as ent

model = hm.Model()

# Suppress GUI for batch performance
hm.setoption(block_redraw=1, command_file_state=0, entity_highlighting=0)
model.hm_blockbrowserupdate(mode=1)

def main():
    # Pre-answer any popups
    model.hm_answernext('yes')
    
    # ... operations ...
    
    result = {"ok": True, ...}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
```
