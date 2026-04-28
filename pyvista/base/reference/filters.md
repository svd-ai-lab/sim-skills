# pyvista Filters

> Applies to: pyvista 0.47

Filters transform meshes or compute derived quantities. They are
methods on `DataSet` instances.

## Geometric filters

```python
surface = grid.extract_surface()            # external boundary → PolyData
edges = grid.extract_feature_edges(60)      # sharp edges
subset = grid.extract_cells([0, 1, 2])     # by cell IDs
subset = grid.extract_points([0, 1, 2])     # by point IDs
```

## Slicing and cutting

```python
slice_z = grid.slice(normal="z", origin=(0, 0, 0.5))
slices  = grid.slice_along_axis(n=5, axis="x")
clipped = grid.clip(normal="x", origin=(0.5, 0, 0))
boxed   = grid.clip_box(bounds=(0, 1, 0, 1, 0, 1))
```

## Thresholding

```python
# Keep cells where scalar in [0.3, 0.7]
hot = grid.threshold([0.3, 0.7], scalars="Temperature")

# Just lower bound
nonzero = grid.threshold(0.0, invert=False, scalars="Velocity")
```

## Iso-surfaces / contours

```python
iso = grid.contour(isosurfaces=10, scalars="Temperature")
iso = grid.contour(isosurfaces=[0.1, 0.5, 0.9], scalars="Temperature")
```

## Compute derived quantities

```python
# Per-cell sizes (length, area, volume)
sized = grid.compute_cell_sizes()
total_volume = sized.cell_data["Volume"].sum()
total_area   = sized.cell_data["Area"].sum()

# Surface area (only meaningful for PolyData)
area = polydata.area

# Volume (closed surface or cell-averaged)
volume = polydata.volume

# Centroid
centroid = grid.center
```

## Scalar field operations

```python
# Gradient of a scalar field
grid = grid.compute_derivative(scalars="Temperature")   # adds "gradient"

# Vector magnitude
grid["speed"] = np.linalg.norm(grid["Velocity"], axis=1)

# Simple math on arrays
grid["T_kelvin"] = grid["T_celsius"] + 273.15
```

## Streamlines (for vector fields)

```python
stream = grid.streamlines(
    vectors="Velocity",
    n_points=100,
    source_radius=0.1,
    source_center=(0, 0, 0),
    max_time=100.0,
)
```

## Sampling / probing

```python
# Sample grid values onto specific points
probe_points = pv.PolyData([[0.5, 0.5, 0.5], [1, 1, 1]])
probe = probe_points.sample(grid)
# probe["Temperature"] now has values at those 2 points
```

## Boolean operations (PolyData only)

```python
union  = a.boolean_union(b)
diff   = a.boolean_difference(b)
intersect = a.boolean_intersection(b)
```

## Glyphs (vector visualization)

```python
arrows = grid.glyph(orient="Velocity", scale="speed", factor=0.5)
```

## Chain filters

```python
result = (
    grid
    .threshold(0.5, scalars="T")
    .extract_surface()
    .smooth(n_iter=20)
)
```

## Gotchas

- `compute_cell_sizes()` with `volume=True` gives 0 for 2D cells
- `extract_surface` on UnstructuredGrid returns PolyData
- `threshold` with string returns a single-criterion result; use list
  for range
- Most filters return a **new** dataset; they don't modify in place
