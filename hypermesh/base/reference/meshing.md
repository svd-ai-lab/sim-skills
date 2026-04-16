# HyperMesh Meshing Operations

> Applies to: HyperWorks Desktop 2024+

## Surface meshing (2D)

### automesh -- single surface

```python
model.automesh(
    collection=surface_collection,    # Collection of surfaces
    element_size=5.0,                 # Target element size
    # ... additional parameters
)
```

### automesh_mc -- batch via mesh controls

```python
model.automesh_mc(
    collection=surface_collection,
)
```

### batchmesh2 -- interactive batch meshing

```python
model.batchmesh2(
    collection=surface_collection,
)
```

### batchmesh_mc -- batch via controls

```python
model.batchmesh_mc(
    collection=surface_collection,
)
```

## Volume meshing (3D)

### tetmesh -- tetrahedral

```python
solids = hm.Collection(model, ent.Solid)
empty_nodes = hm.Collection(model, ent.Node, populate=False)

params = hm.hwStringList([
    "pars: upd_shell fix_comp_bdr post_cln elem_order = 2 "
    "delaunay el2comp=3 fill_void=1 "
    "tet_clps='0.100000,0.300000,0.500000,1.000000,0.380000,0.100000'",
    "tet: 35 1.3 -1 0.014 0.8 0 0 1",
    "2d: 1 0 4 0.01 0.001 30 1",
])

status = model.tetmesh(
    collection1=solids,
    mode1=1,
    collection2=empty_nodes,
    mode2=5,
    string_array=params,
)
```

## Element quality checks

### Available checks

| Method | What it checks |
|--------|---------------|
| `elementtestaspect()` | Aspect ratio |
| `elementtestskew()` | Skew angle |
| `elementtestjacobian()` | Jacobian ratio |
| `elementtestlength()` | Edge length |
| `elementtestwarpage()` | Warpage angle |
| `elementtestinterangle()` | Interior angle |
| `elementtestequiaskew()` | Equiangle skew |
| `elementtestorthogonality()` | Orthogonality (3D) |
| `elementtestsizeratio()` | Neighbor size ratio (3D) |
| `elementtesttetracollapse()` | Tetra collapse ratio |
| `elementtestvolumetricskew()` | Volumetric skew (tetra) |
| `elementtesttimestep()` | Time step (explicit) |

### Quality check pattern

```python
# Configure quality settings
model.elementchecksettings(...)

# Run checks -- results populate collections
status = model.elementtestaspect(
    collection=elements,
    threshold=5.0,          # Elements with aspect > 5.0 flagged
)

# Get quality summary
status, result = model.getqualitysummary(collection=elements)
```

### Quality improvement

```python
# Smooth nodes to improve quality
model.elementqualitysmoothnodesnew(collection=elements)

# Optimize node positions
model.elementqualityoptimizenodenew(collection=elements)

# Move node to improve quality
model.elementquality_move_node(node=node, x=0.1, y=0.0, z=0.0)

# Collapse edge between elements
model.elementqualitycollapseedge(collection=elements)

# Swap edge connectivity
model.elementqualityswapedgenew(collection=elements)
```

## Boundary layer meshing

```python
# 2D boundary layer mesh
model.blmesh_2d(
    collection=surface_collection,
    # ... BL parameters
)

# Compute BL thickness
model.blmesh_2d_computeblthickness(
    collection=surface_collection,
)
```

## Adaptive wrapping (for CFD external aero)

```python
# Multi-step workflow
model.adaptive_wrapper_init(...)
model.adaptive_wrapper_build(...)
model.adaptive_wrapper_set_params(...)
model.adaptive_wrapper_mesh(...)
model.adaptive_wrapper_leak_check(...)
model.adaptive_wrapper_end(...)
```

## Mesh modification

```python
# Translate elements
model.translatemark(
    collection=hm.Collection(model, ent.Element),
    vector_id=hm.hwTriple(0.0, 0.0, 1.0),
    distance=500.0,
)

# Reflect/mirror mesh
model.reflectmark(
    collection=elements,
    plane_base=[0, 0, 0],
    plane_normal=[1, 0, 0],
)

# Rebuild/remesh
model.rebuild_mesh_advanced(
    collection=elements,
    mode="rebuild",
    keep_selection="failed",
)
```

## Meshing tips for batch scripts

1. **Set element size before meshing:**
   ```python
   hm.setoption(element_size=5.0)
   ```

2. **Use block_redraw for performance:**
   ```python
   hm.setoption(block_redraw=1)
   ```

3. **Check quality after meshing:**
   ```python
   elems = hm.Collection(model, ent.Element)
   status = model.elementtestjacobian(collection=elems, threshold=0.3)
   ```

4. **Pre-answer popups:**
   ```python
   model.hm_answernext('yes')
   ```
