# PyDyna `keywords` API — building `.k` files in Python

## Why use the SDK instead of hand-writing `.k`?

| Hand-written `.k` (KI-004 risk) | PyDyna keywords API |
|---|---|
| 8-character fixed-width fields, easy to misalign | Type-safe Python attributes |
| Card order matters, missing cards silently break parsing | Deck class manages card ordering |
| No IDE autocomplete, no validation | Full IDE support, value validation on attribute set |
| Comments/units must be tracked manually | Each keyword class is self-documenting |

For Category A inputs (BCs, materials, geometry) the SDK path is **strongly preferred**
to avoid keyword card alignment errors.

## Core building blocks

### Deck — the top-level container

```python
from ansys.dyna.core import Deck, keywords as kwd

deck = Deck()
deck.title = "My simulation title"
```

### Keywords — Python classes mirroring `*KEYWORD` cards

The `kwd` namespace contains ~3,173 auto-generated classes from the LS-DYNA
specification. Naming convention: `*MAT_ELASTIC` → `kwd.MatElastic`,
`*CONTROL_TERMINATION` → `kwd.ControlTermination`, etc.

```python
mat = kwd.Mat003(mid=1)        # *MAT_PLASTIC_KINEMATIC (MAT_003)
mat.ro = 7.85e-9               # density
mat.e = 150000.0               # Young's modulus
mat.pr = 0.34                  # Poisson's ratio
mat.sigy = 390.0               # yield stress
mat.etan = 90.0                # tangent modulus
```

You can also use `kwd.MatElastic` (alias by name) instead of `kwd.Mat001`.

### Adding keywords to the deck

```python
deck.append(mat)                    # one at a time
deck.extend([mat, sec, part, ctrl]) # batch
```

Order in the deck is preserved when written, but LS-DYNA itself is mostly
order-independent for definitions (control cards are exceptions).

## Common keyword classes

### Materials
```python
kwd.MatElastic(mid=1, ro=..., e=..., pr=...)               # MAT_001
kwd.Mat003(mid=1, ro=..., e=..., pr=..., sigy=..., etan=...)  # MAT_PLASTIC_KINEMATIC
kwd.MatRigid(mid=1, ...)                                   # MAT_020
```

### Sections
```python
kwd.SectionSolid(secid=1, elform=1)   # 1 = constant stress hex
kwd.SectionShell(secid=1, elform=2, t1=...)
kwd.SectionTShell(secid=1, elform=1, ...)
```

### Parts (associates section + material to elements)
```python
import pandas as pd

# Single part
part = kwd.Part(pid=1, mid=mat.mid, secid=sec.secid)

# Or via DataFrame for multiple parts
part = kwd.Part()
part.parts = pd.DataFrame({
    "pid":   [1, 2, 3],
    "mid":   [1, 2, 1],
    "secid": [1, 1, 2],
})
```

### Nodes and elements (DataFrame-based)
```python
node = kwd.Node()
node.nodes = pd.DataFrame({
    "nid": [1, 2, 3, 4, 5, 6, 7, 8],
    "x":   [0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
    "y":   [0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0],
    "z":   [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0],
})
deck.append(node)

elem = kwd.ElementSolid()
elem.elements = pd.DataFrame({
    "eid": [1], "pid": [1],
    "n1": [1], "n2": [2], "n3": [3], "n4": [4],
    "n5": [5], "n6": [6], "n7": [7], "n8": [8],
})
deck.append(elem)
```

### Boundary conditions
```python
bc = kwd.BoundarySpcNode()
bc.nodes = pd.DataFrame({
    "nid":   [1, 2, 3, 4],
    "cid":   [0, 0, 0, 0],
    "dofx":  [1, 1, 1, 1],
    "dofy":  [1, 1, 1, 1],
    "dofz":  [1, 1, 1, 1],
    "dofrx": [0, 0, 0, 0],
    "dofry": [0, 0, 0, 0],
    "dofrz": [0, 0, 0, 0],
})
```

### Loads and curves
```python
curve = kwd.DefineCurve(lcid=1)
curve.curves = pd.DataFrame({"a1": [0.0, 0.1, 1.0], "o1": [0.0, 1.0, 1.0]})

load = kwd.LoadNodePoint()
load.loads = pd.DataFrame({
    "nid": [5, 6, 7, 8],
    "dof": [3, 3, 3, 3],
    "lcid": [1, 1, 1, 1],
    "sf": [0.0025, 0.0025, 0.0025, 0.0025],
})
```

### Initial conditions
```python
init_vel = kwd.InitialVelocityGeneration()
init_vel.id = part.pid
init_vel.styp = 2     # 2 = part
init_vel.vy = 300e3   # mm/s
init_vel.icid = cs.cid
```

### Sets and boxes
```python
box = kwd.DefineBox(boxid=1, xmn=-500, xmx=500, ymn=39.0, ymx=40.1, zmn=-500, zmx=500)
node_set = kwd.SetNodeGeneral(sid=1, option="BOX", e1=box.boxid)
```

### Contact and rigid wall
```python
wall = kwd.RigidwallPlanar(id=1)
wall.nsid = node_set.sid
wall.yt = 40.0
wall.yh = 39.0
```

### Control cards
```python
kwd.ControlTermination(endtim=8.0e-5, dtmin=0.001)
kwd.ControlTimestep(dtinit=0.0, tssfac=0.9)
kwd.ControlImplicitGeneral(imflag=1, dt0=1e-3)
```

### Database output
```python
kwd.DatabaseGlstat(dt=8e-8, binary=3)
kwd.DatabaseMatsum(dt=8e-8, binary=3)
kwd.DatabaseNodout(dt=8e-8, binary=3)
kwd.DatabaseElout(dt=8e-8, binary=3)
kwd.DatabaseRwforc(dt=8e-8, binary=3)
kwd.DatabaseBinaryD3Plot(dt=4e-6)
kwd.DatabaseHistoryNodeSet(id1=node_set.sid)
```

### Including external files
```python
deck.append(kwd.Include(filename="taylor_bar_mesh.k"))
```

## Writing the deck to a file

```python
# Method 1: write to string then save
deck_string = deck.write()
with open("input.k", "w") as f:
    f.write(deck_string)

# Method 2: export directly (preferred)
deck.export_file("input.k")
```

## Previewing geometry (3D)

Requires `pyvista`:
```python
deck.plot()                              # opens interactive 3D window
deck.plot(jupyter_backend="static")      # screenshot in Jupyter
deck.plot(color="lightblue", show_edges=True)  # custom styling
```

## Tip: inspect any keyword's serialized form

```python
shell = kwd.SectionTShell()
print(shell)
# *SECTION_TSHELL
# $#   secid    elform      shrf       nip     propt        qr     icomp    tshear
#                    1       1.0         2       1.0         0         0         0
```

This is invaluable for debugging — you see exactly what will be written to the `.k` file.

## When NOT to use the SDK

- Migrating an existing complex `.k` file from a customer/upstream — read it
  with `Deck.import_file("legacy.k")`, modify what you need, write back. Don't
  rebuild from scratch.
- Mesh files (`*NODE` + `*ELEMENT_*` lists) — these are usually generated by
  meshing tools (ANSA, ICEM, Workbench Meshing). Use `kwd.Include(filename=...)`
  to reference them, don't try to rebuild meshes via the API.
