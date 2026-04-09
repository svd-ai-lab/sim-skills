# YouTube ANSA API Video Research

Fetched 2026-04-03. YouTube renders content via JavaScript so full transcripts could not
be extracted by WebFetch. Below is everything recovered from oEmbed metadata, web searches,
and supplementary sources found during the research.

---

## Video 1: "15 Minutes to ANSA API"

- **URL:** https://www.youtube.com/watch?v=QAl_Mh35hco
- **Channel:** BETA CAE Systems (@Beta-caeGr)
- **Title:** 15 Minutes to ANSA API
- **Description:** Not extractable (YouTube JS-rendered page). Based on the title and
  channel, this is an official BETA CAE Systems quick-start introduction to the ANSA
  Python API.

### Likely Content (based on official BETA CAE training materials)

BETA CAE offers an "Introduction to ANSA scripting" training course whose syllabus
(from beta-cae.com/courses/ansa_scripting_basic.pdf -- 403 protected) covers:

- Python Introduction and basic programming concepts
- ANSA Scripting Introduction: keywords, modules, interacting with entities
- The ANSA Python modules: `ansa.base`, `ansa.guitk`, `ansa.constants`, `ansa.mesh`,
  `ansa.session`, `ansa.utils`
- Creating custom GUIs with ANSA's BC widget toolkit
- Managing entity data (collect, create, modify, delete)

The "Scripting with ANSA" training page (beta-cae.us) lists prerequisites:
basic Finite Element knowledge, ANSA Interface familiarity, programming logic concepts.

---

## Video 2: "Automation with ANSA (Part - 2) | Skill-Lync Workshop"

- **URL:** https://www.youtube.com/watch?v=_nbBIUY9QHY
- **Channel:** Skill Lync (@SkillLync)
- **Title:** Automation with ANSA (Part - 2) | Skill-Lync Workshop
- **Description:** Not extractable. Part of a multi-part workshop series on ANSA automation.
  Part 1 is listed at: https://skill-lync.com/-engineering-workshop/automation-with-ansa-part-1-skill-lync-workshop

### Related Course Information

Skill-Lync offers a "Master's in Automation and Pre-Processing for FEA & CFD Analysis"
which covers ANSA GUI tools, morphing techniques, and automation processes for
pre-processing in ANSA. The workshop series covers Python scripting within the ANSA
environment for automating mesh preprocessing tasks.

---

## Video 3: ANSA Scripting Playlist

- **URL:** https://www.youtube.com/playlist?list=PLtJ-S1Lq-AvtP5o5XeGsHrJl7ujAe2Zr-
- **Note:** Playlist page also rendered via JS; individual video titles could not be
  extracted. The playlist appears to be from BETA CAE Systems and contains multiple
  ANSA scripting tutorial videos. BETA CAE notes they add new tutorial videos weekly.

---

## ANSA Python API Reference (from Scribd + GitHub sources)

### Core Modules

```
import ansa
from ansa import base, mesh, constants, guitk, session, utils
```

### Key `ansa.base` Functions

| Function | Purpose |
|---|---|
| `base.CollectEntities(deck, container, type, ...)` | Collect entities from database. Supports `filter_visible=True`, `prop_from_entities=True` |
| `base.CreateEntity(deck, type, fields_dict)` | Create a new entity with given card values |
| `base.SetEntityCardValues(deck, entity, fields_dict)` | Modify entity properties via label-value pairs |
| `base.GetEntityCardValues(deck, entity, fields_list)` | Read entity card values |
| `base.CollectNewModelEntities()` | Track newly created/imported entities |
| `base.Name2Ents(regex)` | Filter entities by name using regex |
| `base.SetEntityId(entity, new_id, ...)` | Change entity ID |
| `base.AddToSet(set_entity, entity_list)` | Add entities to a SET |
| `base.PickEntities(deck, type, ...)` | Interactive entity picking |
| `base.NodesToElements(node_id)` | Get elements connected to a node |
| `base.CollectBoundaryNodes(part, flag)` | Collect boundary nodes of a part |
| `base.SetViewButton(settings_dict)` | Control view settings (e.g. `{"SHADOW":"on","MACROs":"off"}`) |
| `base.CurrentDeck()` | Get current solver deck |
| `base.SetCurrentDeck(deck)` | Set current solver deck |
| `base.Open(filepath)` | Open an ANSA file |
| `base.SaveAs(filepath)` | Save as ANSA file |
| `base.InputLSDyna(filepath)` | Import LS-DYNA file |
| `base.Compress(arg)` | Compress/clean database |
| `base.CompressMaterials(deck, container, ...)` | Remove duplicate materials |
| `base.DeleteCurves(scope, flag)` | Delete curves |
| `base.PointsDelete(scope)` | Delete points |
| `base.CheckAndFixPenetrations(type, fast_run, fix, ...)` | Check/fix intersections and penetrations |
| `base.CalculateOffElements(comp)` | Calculate off-quality elements (returns dict with `'TOTAL OFF'`) |
| `base.ElementQuality(elem, criterion)` | Get element quality metric (e.g. `"SKEW"`) |
| `base.SetPickMethod(method)` | Set entity pick method |

### Entity Object Methods

```python
entity = base.CollectEntities(deck, None, "PSHELL")[0]

# Get card values (dict-style)
vals = entity.get_entity_values(deck, {'T', 'PID', 'Name'})
# Returns: {'T': 1.5, 'PID': 100, 'Name': 'part_1'}

# Set card values
entity.set_entity_values(deck, {'T': 2.0, 'Name': 'new_name'})

# Entity attributes
entity._id      # Entity ID
entity._name    # Entity name
entity._type    # Entity type code (e.g. 513=CQUAD4, 517=CTRIA3)
```

### Key `ansa.mesh` Functions

| Function | Purpose |
|---|---|
| `mesh.FixQuality()` | Automatically fix mesh quality issues |
| `mesh.ReconstructViolatingShells(expand_level)` | Reconstruct shells violating quality criteria |

### Key `ansa.constants` Constants

| Constant | Purpose |
|---|---|
| `constants.NASTRAN` | Nastran solver deck |
| `constants.LSDYNA` | LS-DYNA solver deck |
| `constants.FLUENT` | Fluent solver deck |

### Key `ansa.guitk` Functions (GUI Toolkit)

| Function | Purpose |
|---|---|
| `guitk.BCWindowCreate(title, flags)` | Create a window |
| `guitk.BCPushButtonCreate(parent, label, callback, data)` | Create a push button |
| `guitk.BCBoxLayoutCreate(parent, orientation)` | Create a layout |
| `guitk.BCLabelCreate(parent, text)` | Create a label |
| `guitk.BCLineEditCreateInt(parent, default)` | Create integer input field |
| `guitk.BCLineEditGetInt(widget)` | Get integer from input |
| `guitk.BCTableCreate(parent, rows, cols)` | Create a table widget |
| `guitk.BCTableSetNumRows(table, n)` | Set table row count |
| `guitk.BCTableHeaderSetLabel(table, orient, idx, text)` | Set table header label |
| `guitk.BCTableSetText(table, row, col, text)` | Set table cell text |
| `guitk.BCTableSetColumnAlignment(table, col, align)` | Set column alignment |
| `guitk.BCTableSetReadOnly(table, flag)` | Set table read-only |
| `guitk.BCMessageWindowCreate(type, msg, flag)` | Create message dialog |
| `guitk.BCMessageWindowSetRejectButtonVisible(w, flag)` | Hide reject button |
| `guitk.BCWindowFlash(window)` | Flash window |
| `guitk.BCWindowSetAcceptFunction(window, callback, data)` | Set OK callback |
| `guitk.BCWindowSetRejectFunction(window, callback, data)` | Set Cancel callback |
| `guitk.BCWindowShowTitleBarButtons(window, flags)` | Configure title bar |
| `guitk.BCShow(widget)` | Show a widget |
| `guitk.UserWarning(message)` | Show warning dialog |

#### guitk Constants
- `guitk.constants.BCOnExitDestroy`
- `guitk.constants.BCMinimizeButton`, `BCMaximizeButton`
- `guitk.constants.BCHorizontal`, `BCVertical`
- `guitk.constants.BCAlignRight`
- `guitk.constants.BCMessageBoxWarning`

#### Additional guitk Widgets (from Scribd API doc)
- **BCSpinBox** -- numerical input with up/down controls within set limits
- **BCLineEdit** -- text/number input
- **BCTabWidget** -- tabbed interface for organizing settings
- **BCListView** -- interactive list with checkboxes, double-click editing
- **BCWidgetStack** -- dynamic content swapping (e.g. between BCLineEditPath and BCProgressBar)

### Key `ansa.session` Functions

| Function | Purpose |
|---|---|
| `session.New('discard')` | New session, discard current |
| `ansa.session.defbutton(toolbar, label)` | Decorator to register script as toolbar button |

### Key `ansa.utils` Functions

| Function | Purpose |
|---|---|
| `utils.SelectOpenFileIn(path, flag)` | File open dialog |

### Special Entity Type Strings

- `"__PROPERTIES__"` -- all property types
- `"__ELEMENTS__"` -- all element types
- `"SHELL"` / `"ELEMENT_SHELL"` -- shell elements (Nastran / LS-DYNA)
- `"GRID"` / `"NODE"` -- grid/node entities
- `"PSHELL"` / `"SECTION_SHELL"` -- shell property
- `"ANSAPART"` -- ANSA part entity
- `"SET"` -- entity set

---

## Complete Code Examples from GitHub

### Example 1: Automated Skewed Element Removal (vahadruya)

Source: https://github.com/vahadruya/Basic_Python_Script_in_ANSA_for_Automated_Handling_of_Skewed_Elements

```python
import os
import ansa
from ansa import mesh, base, constants
import time

def main():
    comp_array = base.CollectEntities(constants.FLUENT, None, "__PROPERTIES__")
    total_off = sum([base.CalculateOffElements(comp)['TOTAL OFF'] for comp in comp_array])
    print('Total number of OFF elements = ', total_off)

    def offs_per_comp(comp, ind=0):
        id = int(str(comp).split(':')[-1].split('>')[0])
        try:
            component_off = base.CalculateOffElements(comp)['TOTAL OFF']
            elem_count = len(base.CollectEntities(constants.FLUENT, comp, "__ELEMENTS__"))
            percent_off = (component_off*100)/elem_count
            print(f'Total number of OFF elements in component {id}\t:\t{component_off} ({round(percent_off, 5)}%)')
        except:
            print(f'This component ({id}) has no elements')

    for ind_, comp_ in enumerate(comp_array):
        offs_per_comp(comp_, ind_)

    # Phase 1: Fix Quality method
    n_off = 1.1
    while total_off != n_off:
        n_off = total_off
        mesh.FixQuality()
        total_off = sum([base.CalculateOffElements(comp)['TOTAL OFF'] for comp in comp_array])

    print('\nFIX QUALITY METHOD')
    print('Total number of OFF elements = ', total_off)
    if total_off != 0:
        for ind_, comp_ in enumerate(comp_array):
            offs_per_comp(comp_, ind_)

    # Phase 2: Reconstruct method (escalating expand levels)
    i = 0
    while total_off != 0:
        if i == 0:
            print('\nMESH RECONSTRUCT METHOD')
        print(f'\nExpand Level : {i}')
        mesh.ReconstructViolatingShells(i)
        i += 1
        total_off = sum([base.CalculateOffElements(comp)['TOTAL OFF'] for comp in comp_array])
        print('Total number of OFF elements = ', total_off)
        if total_off != 0:
            for ind_, comp_ in enumerate(comp_array):
                offs_per_comp(comp_, ind_)

    def compute_skews():
        elems = base.CollectEntities(constants.FLUENT, None, "__ELEMENTS__")
        qual = [base.ElementQuality(elem, "SKEW") for elem in elems]
        skews = [elem for elem in qual if elem >= 0.6]
        return max(qual), len(skews)

    skew_info = compute_skews()
    print(f'\nProcess Complete.\nTotal Skew = {skew_info[1]}\nMaximum Skew = {skew_info[0]}\n')

start = time.time()
main()
print(f'Time taken for code completion: {round(time.time() - start, 4)} seconds\n')
```

### Example 2: Free Edge Detection (sshnuke333)

Source: https://github.com/sshnuke333/ANSA-Scripts/blob/master/Free_Edge.py

```python
import os
import random
import ansa
from ansa import base, guitk, constants

@ansa.session.defbutton("MISC", "FREE EDGE")
def Free_Edge():
    deck = constants.NASTRAN
    set_check = base.CollectEntities(deck, None, "SET")
    for set in set_check:
        if set.get_entity_values(deck, {'Name'}) == {'Name': 'Free Edge'}:
            guitk.UserWarning("SET named Free Edge already exists")
            return 1

    parts = base.CollectEntities(deck, None, "ANSAPART", filter_visible=True)
    idlist = []
    element_list = []
    final = []

    # Collect boundary node IDs from visible parts
    for part in parts:
        nodes = base.CollectBoundaryNodes(part, False)
        ids = nodes.perimeters
        for id in ids:
            for x in id:
                idlist.append(x._id)

    # Collect elements from node list
    for id in idlist:
        ans = base.NodesToElements(id)
        for key, data in ans.items():
            for x in data:
                element_list.append(x)

    # Remove duplicates, find elements with 2+ free edges
    # ... (logic checks adjacent node element connectivity)

    set = base.CreateEntity(deck, 'SET', {'Name': 'Free Edge'})
    base.AddToSet(set, final)
```

### Example 3: Master/Slave PID Table (sshnuke333)

Source: https://github.com/sshnuke333/ANSA-Scripts/blob/master/Master_Slave.py

```python
import ansa
from ansa import base, guitk, constants

@ansa.session.defbutton("MISC", "MASTER_SLAVE")
def master_slave():
    deck = constants.NASTRAN
    prop = '__PROPERTIES__'

    base.SetPickMethod(base.constants.ENT_SELECTION)
    list = base.PickEntities(deck, prop, filter_visible=True, prop_from_entities=True)

    master_list = []
    slave_list = []
    for i in range(0, len(list)):
        if (i % 2) == 0 or i == 0:
            master = list[i].get_entity_values(deck, {'PID'})
            master_list.append(master['PID'])
        elif (i % 2) == 1:
            slave = list[i].get_entity_values(deck, {'PID'})
            slave_list.append(slave['PID'])

    # Display in GUI table
    window = guitk.BCWindowCreate("Master Slave Table", guitk.constants.BCOnExitDestroy)
    table = guitk.BCTableCreate(window, 2, 2)
    guitk.BCTableSetNumRows(table, len(master_list))
    guitk.BCTableHeaderSetLabel(table, guitk.constants.BCHorizontal, 0, 'Master')
    guitk.BCTableHeaderSetLabel(table, guitk.constants.BCHorizontal, 1, 'Slave')
    for i in range(len(master_list)):
        guitk.BCTableSetText(table, i, 0, str(master_list[i]))
    for i in range(len(slave_list)):
        guitk.BCTableSetText(table, i, 1, str(slave_list[i]))
    guitk.BCShow(window)
```

### Example 4: FE Counter / PID Renaming (sshnuke333)

Source: https://github.com/sshnuke333/ANSA-Scripts/blob/master/FE_Counter.py

Key patterns demonstrated:
- `@ansa.session.defbutton("Elements", "Counter")` for toolbar registration
- `session.New('discard')` to start fresh session
- `base.Open(file)` / `base.SaveAs(path)` for file I/O
- `base.InputLSDyna(file)` for LS-DYNA import
- `base.SetCurrentDeck(constants.NASTRAN)` / `base.SetCurrentDeck(constants.LSDYNA)`
- Entity card value get/set with `entity.get_entity_values()` / `entity.set_entity_values()`
- `base.SetViewButton()` for view control
- `base.Compress('')` for database cleanup
- `base.CompressMaterials()` for duplicate material removal
- `base.CheckAndFixPenetrations()` for geometry checks

### Example 5: mesh2vec ANSA Data Extraction (Renumics)

Source: https://renumics.github.io/mesh2vec/customize_ansa_script.html

```python
import json
from ansa import constants, base

# Load LS-DYNA file
base.InputLSDyna(filepath)

# Collect parts and filter
parts = base.CollectEntities(constants.LSDYNA, None, "__PROPERTIES__")

# Extract shell elements with quality metrics:
#   __id__, type, EID, PID, N1-N4, __part__
#   Plus: warpage, aspect ratio, skew, area, normal vectors

# Extract node coordinates:
#   __id__, X, Y, Z

# Export as JSON
```

---

## qd-ansa-extension Library (Community Wrapper)

Source: https://github.com/qd-cae/qd-ansa-extension

Provides a more Pythonic wrapper around the ANSA API:

```python
from qd.ansa import QDEntity

# Create entity
entity = QDEntity.create("NODE", constants.NASTRAN, X1=0.0, X2=20.0, X3=0.0)

# Get entity by ID
entity = QDEntity.get("NODE", 1)

# Dict-like access
entity["X1","X2","X3"]              # Returns [0.0, 20.0, 0.0]
entity["X1","X2","X3"] = [1., 19., 1.]  # Set values

# Collect entities
entities = QDEntity.collect("NODE", container, constants.NASTRAN)

# Iterate card values
for key, value in entity:
    print(key, value)

# List all cards
entity.cards()   # or entity.keys()
entity.values()

# Interactive edit
entity.user_edit()
```

### META Export
```python
from qd.meta.export import export_to_html
export_to_html("output.html", use_fringe=True, fringe_bounds=[0, 0.03])
```

---

## Scribd Document: "ANSA API Tasks and Explanations"

- **Author:** Srinivas Nadella
- **URL:** https://www.scribd.com/document/904983544/ANSA-API-Tasks-and-Explanations
- **Content:** Python API manipulation for ANSA including tasks such as:
  - Assigning failure values based on SIGY
  - Collecting spot welds
  - Renumbering IDs
  - Replacing characters in PID names
  - Setting element forms for solid and shell elements
  - Usage of `base.CollectEntities()`

(Full document content not extractable from Scribd's JS-rendered viewer.)

---

## BETA CAE Conference Paper: Python Scripting in ANSA/META

- **Source:** 7th BEFORE REALITY CONFERENCE
- **Paper:** "PYTHON SCRIPTING IN ANSA/META FOR AUTOMATED TASKS"
- **Author:** UZUN et al.
- **URL:** https://www.beta-cae.com/events/c7pdf/10A_2_UZUN.pdf (403 protected)

---

## BETA CAE Conference Paper: ANSA Scripting for Automated Pedestrian Protection

- **Source:** 6th BETA CAE International Conference
- **Author:** OPEL (Opel Automobile GmbH)
- **URL:** https://www.beta-cae.com/events/c6pdf/4A_2_OPEL.pdf (403 protected)

---

## Summary of ANSA Python API Architecture

```
ansa (top-level package)
  |-- base          Core entity operations (collect, create, modify, delete, I/O)
  |-- mesh          Meshing operations (fix quality, reconstruct, auto-mesh)
  |-- guitk         GUI toolkit (windows, buttons, tables, dialogs, layouts)
  |-- constants     Solver deck constants (NASTRAN, LSDYNA, FLUENT, etc.)
  |-- session       Session management (new, defbutton decorator)
  |-- utils         Utility functions (file dialogs)
```

### Common Script Pattern

```python
import ansa
from ansa import base, mesh, constants, guitk

# 1. Register as toolbar button
@ansa.session.defbutton("ToolbarName", "ButtonLabel")
def my_script():
    # 2. Set solver deck
    deck = constants.NASTRAN

    # 3. Collect entities
    entities = base.CollectEntities(deck, None, "PSHELL", filter_visible=True)

    # 4. Read/modify card values
    for ent in entities:
        vals = ent.get_entity_values(deck, {'T', 'Name'})
        ent.set_entity_values(deck, {'Name': 'modified_' + vals['Name']})

    # 5. Create new entities
    new_set = base.CreateEntity(deck, 'SET', {'Name': 'MySet'})
    base.AddToSet(new_set, entities)

    # 6. Optional GUI
    window = guitk.BCWindowCreate("Result", guitk.constants.BCOnExitDestroy)
    guitk.BCShow(window)
```
