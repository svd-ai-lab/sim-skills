# HyperMesh Entities and Collections

> Applies to: HyperWorks Desktop 2024+

## Collections -- the core selection mechanism

Collections replace Tcl-style "marks" in the Python API. They are
persistent, composable, and iterable.

### Creation patterns

```python
import hm
import hm.entities as ent

model = hm.Model()

# 1. All entities of a type
all_elems = hm.Collection(model, ent.Element)

# 2. Empty collection
empty = hm.Collection(model, ent.Element, populate=False)

# 3. By ID list
specific = hm.Collection(model, ent.Element, [1, 2, 3, 4, 5])

# 4. By ID range
range_col = hm.Collection(model, ent.Element, list(range(1, 101)))

# 5. By attribute expression
thick_shells = hm.Collection(model, ent.Property, "PSHELL_T>2.0")
steel_mats = hm.Collection(model, ent.Material, 'name="steel"')

# 6. By parent collection (elements by component)
comp_col = hm.Collection(model, ent.Component, [1])
comp_elems = hm.Collection(model, ent.Element, comp_col)

# 7. By filter objects
fil = hm.FilterByEnumeration(ent.Property, [103, 104, 201, 202])
props = hm.Collection(model, fil)
```

### FilterBy classes

| Class | Purpose | Example |
|-------|---------|---------|
| `FilterByAttribute` | By attribute value | `FilterByAttribute(ent.Material, "Nu<0.3")` |
| `FilterByEnumeration` | By ID list | `FilterByEnumeration(ent.Element, [1,2,3])` |
| `FilterByCollection` | By parent entities | `FilterByCollection(ent.Element, ent.Property)` |
| `FilterByBox` | By bounding box | `FilterByBox(ent.Element, [0,0,0], [10,10,10])` |
| `FilterBySphere` | By sphere region | `FilterBySphere(ent.Node, [0,0,0], 5.0)` |
| `FilterByCylinder` | By cylinder region | `FilterByCylinder(ent.Node, base, normal, r, h)` |
| `FilterByCone` | By cone region | `FilterByCone(ent.Node, base, normal, r1, r2, h)` |
| `FilterByPlane` | By plane distance | `FilterByPlane(ent.Element, base, normal, tol=1.0)` |

### Collection operations

```python
# Union
combined = col1 + col2

# Difference
remaining = col1 - col2

# Add single entity
col = col + entity_obj

# Iteration
for elem in collection:
    print(elem.id, elem.config)

# Length
count = len(collection)

# Bulk get attribute values
ids = collection.get_values("id")         # numpy array
names = collection.get_values("name")     # Python list

# Bulk set attribute values
collection.set_values("propertyid", prop)
```

### CollectionByAdjacent / CollectionByAttached

```python
# Elements adjacent to element 579
source = hm.Collection(model, ent.Element, [579])
adjacent = hm.CollectionByAdjacent(model, source)

# Elements attached (connected) to element 579
attached = hm.CollectionByAttached(model, source)

# Elements on same face
face_elems = hm.CollectionByFace(model, source)
```

### CollectionSet (multi-type input)

```python
colset = hm.CollectionSet(model)
colset.set(hm.Collection(model, ent.Element))
colset.set(hm.Collection(model, ent.Node))
# Pass to functions that accept multiple entity types
```

## Entity attributes

```python
# Read attributes
elem = ent.Element(model, 100)
config = elem.config          # Element config (e.g., 104 = QUAD4)
jacobian = elem.jacobian      # Jacobian ratio
area = elem.area              # Element area
prop = elem.propertyid        # Property entity reference

# Write attributes
mat = ent.Material(model)
mat.name = "Aluminum"
mat.cardimage = "MAT1"
mat.E = 70000.0               # Young's modulus
mat.Nu = 0.33                 # Poisson's ratio
mat.Rho = 2.7e-9              # Density

prop = ent.Property(model)
prop.cardimage = "PSHELL"
prop.materialid = mat          # Assign material
prop.PSHELL_T = 1.5            # Shell thickness
```

## Common entity configurations

### Element configs

| Config | Type | Nodes |
|--------|------|-------|
| 103 | TRIA3 | 3 |
| 104 | QUAD4 | 4 |
| 204 | TETRA4 | 4 |
| 208 | HEXA8 | 8 |
| 206 | PENTA6 | 6 |

### Load configs

| Config | Type |
|--------|------|
| 1 | Force (LoadForce) |
| 2 | Moment (LoadMoment) |
| 3 | Constraint/SPC (LoadConstraint) |
| 4 | Pressure (LoadPressure) |
| 5 | Temperature (LoadTemperature) |

## Data types (implicit conversion)

Python lists auto-convert to HyperMesh types:

| HyperMesh | Python equivalent |
|-----------|-------------------|
| `hwTriple` | `[x, y, z]` (3 floats) |
| `hwDoubleList` | `[1.0, 2.0, 3.0]` |
| `hwIntList` | `[1, 2, 3]` |
| `hwStringList` | `["a", "b", "c"]` |
| `hwString` | `"text"` |
| `EntityList` | `[entity1, entity2]` |
