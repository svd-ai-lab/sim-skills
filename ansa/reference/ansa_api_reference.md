# ANSA Python API Reference for sim

## Overview

BETA CAE ANSA's Python API (`ansa` module) is only available inside the ANSA process.
Scripts are executed via `ansa_win64.exe -execscript "script.py|main()" -nogui`.

**Execution model**: One-shot batch. No persistent sessions, no external RPC/socket API.

## Core Modules

| Module | Purpose |
|--------|---------|
| `ansa.base` | Entity management, file I/O, quality checks, transforms |
| `ansa.mesh` | Mesh generation, quality repair, reconstruction |
| `ansa.constants` | Solver deck constants (`NASTRAN`, `FLUENT`, `LSDYNA`, `ABAQUS`, etc.) |
| `ansa.session` | Session control (`New`, `defbutton`), GUI button registration |
| `ansa.utils` | File dialogs, utility functions |
| `ansa.guitk` | GUI widget toolkit (windows, buttons, tables) — **GUI only, fails with -nogui** |

## Script Convention for sim

```python
import json
import ansa
from ansa import base, constants

def main():
    """Entry point for ansa_win64.exe -execscript 'script.py|main()'."""
    deck = constants.NASTRAN  # or FLUENT, LSDYNA, ABAQUS, etc.

    # ... operations ...

    result = {"status": "ok", "element_count": 12345}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
```

Rules:
- Define `main()` as entry point (required by `-execscript "script.py|main()"`)
- Print a single JSON line to stdout as last output (sim `parse_output()` extracts it)
- Use `session.New('discard')` before `base.Open()` to start clean
- **Never use** `guitk`, `PickEntities`, `UserInput` in batch mode

## Common API Patterns

### Collecting Entities

```python
# All shells in model
shells = base.CollectEntities(deck, None, "SHELL")

# All visible elements
visible = base.CollectEntities(deck, None, "SHELL", filter_visible=True)

# Elements under a specific property/component
elems = base.CollectEntities(deck, comp, "__ELEMENTS__")

# All properties
props = base.CollectEntities(deck, None, "__PROPERTIES__")

# All grid/nodes
grids = base.CollectEntities(deck, None, "GRID")
```

**Common pitfall**: Second argument must be `None` (global) or an iterable of entities.
`TypeError: CollectEntities: argument 2 must be an iterable` — most common beginner error.

### Reading/Writing Entity Values

```python
# Get values (returns dict)
vals = entity.get_entity_values(deck, {'T', 'PID', 'Name'})
thickness = vals['T']

# Alternative: card-based access
coords = base.GetEntityCardValues(deck, node, ('X', 'Y', 'Z'))

# Set values
entity.set_entity_values(deck, {'Name': 'new_name', 'T': 2.5})
base.SetEntityCardValues(deck, entity, {'Thickness': 2.5})
```

### Entity Properties

```python
entity._id    # numeric ID
entity._name  # string name
entity._type  # type code (e.g., 513=QUAD, 517=TRIA)
```

### File I/O

```python
session.New('discard')           # Clear current model
base.Open('/path/to/model.ansa') # Open ANSA database
base.SaveAs('/path/out.ansa')    # Save as new file

# Import solver decks
base.InputNastran('/path/to/file.nas')
base.InputLSDyna('/path/to/file.key')

# Output solver decks
base.OutputNastran('/path/to/out.nas')
base.OutputLSDyna('/path/to/out.key')
```

### Element Quality

```python
quality = base.ElementQuality(elem, "SKEW")    # Single element
off_info = base.CalculateOffElements(comp)      # Returns {'TOTAL OFF': n}
```

### Mesh Operations

```python
mesh.FixQuality()                          # Auto-fix quality violations
mesh.ReconstructViolatingShells(level)     # Reconstruct at expand level (0, 1, 2...)
```

### Entity Creation and Modification

```python
# Create entity
new_set = base.CreateEntity(deck, 'SET', {'Name': 'MySet'})
base.AddToSet(new_set, elements)

# Change entity ID
base.SetEntityId(entity, new_id, True, False)

# Delete/compress
base.Compress('')
base.CompressMaterials(deck, None, 1, 1, 1)
base.DeleteCurves('all', True)
base.PointsDelete('all')
```

### Intersection/Penetration Checks

```python
intersections = base.CheckAndFixPenetrations(type=1, fast_run=False, fix=False)
penetrations = base.CheckAndFixPenetrations(type=3, fast_run=False, fix=False, user_thic=0.6)
```

### Other Useful Functions

```python
base.CollectNewModelEntities()  # Track newly created entities
base.Name2Ents(pattern)         # Find entities by name (regex)
base.CurrentDeck()              # Get active solver deck
base.SetCurrentDeck(deck)       # Switch solver deck
base.SetViewButton({...})       # Control viewport visibility
```

## Solver Deck Constants

```python
constants.NASTRAN    # Nastran
constants.ABAQUS     # Abaqus
constants.LSDYNA     # LS-DYNA
constants.FLUENT     # Fluent
constants.PAMCRASH   # PAM-CRASH
constants.RADIOSS    # Radioss
constants.OPTISTRUCT # OptiStruct
constants.PERMAS     # Permas
```

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| `CollectEntities` arg 2 not iterable | Use `None` for global scope, not a single entity |
| Forgetting to set deck | Always specify `deck = constants.NASTRAN` (or appropriate) |
| GUI functions in batch mode | Avoid `guitk.*`, `PickEntities`, `UserInput` — use `-nogui` safe alternatives |
| Deck mismatch | Entity operations must match the deck the model was loaded with |
| Path with spaces | Quote all file paths; use forward slashes on Windows |
| `ANSA_SRV` not set | Must be set to license server before launch (default: `ansa_srv.localdomain`) |
| Script output captured wrong | Print JSON as the **last** stdout line for `parse_output()` |

## Execution Environment

### Required Environment Variables

```
ANSA_SRV=localhost                   # License server
BETA_SHARED_DIR=<install>/shared_v25.0.0/
PYTHONHOME=<shared>/python/win64/
ANSA_HOME=<install>/ansa_v25.0.0/config/
HDF5_DISABLE_VERSION_CHECK=2
QTDIR=<shared>/win64
QT_PLUGIN_PATH=<shared>/win64/plugins
```

### Invocation

```
ansa_win64.exe -execscript "script.py|main()" -nogui
```

For scripts without `main()`:
```
ansa_win64.exe -exec "load_script: 'script.py'" -nogui
```

## Sources

- ANSA v25.0.0 built-in scripting help (Help > Scripting Help)
- BETA CAE Open Meeting presentations
- GitHub: sshnuke333/ANSA-Scripts (FE_Counter, Free_Edge, Master_Slave)
- GitHub: vahadruya/Basic_Python_Script (Skewed Elements)
- Opel/BETA CAE: ANSA Scripting for Pedestrian Marking (conference paper)
- CFD-Online Forums, Stack Overflow community Q&A
