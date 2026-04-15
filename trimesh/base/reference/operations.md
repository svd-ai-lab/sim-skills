# Mesh operations

## Boolean (CSG)

Requires a backend: `manifold3d` (pure-pip, recommended), `scad`, or `blender`.

```python
a = trimesh.creation.box(extents=[2, 2, 2])
b = trimesh.creation.icosphere(radius=1.2)

a_minus_b = a.difference(b)        # subtraction
a_or_b    = a.union(b)             # union
a_and_b   = a.intersection(b)      # intersection
```

## Ray casting

```python
ray_origins    = [[0, 0, -10]]
ray_directions = [[0, 0, 1]]

locations, ray_idx, tri_idx = m.ray.intersects_location(
    ray_origins=ray_origins, ray_directions=ray_directions,
)
hits = m.ray.intersects_first(
    ray_origins=ray_origins, ray_directions=ray_directions,
)
```

## Point sampling

```python
points, face_idx = trimesh.sample.sample_surface(m, count=10000)
points_uniform   = m.sample(count=1000)               # alias of above
inside           = m.contains(points_uniform)         # signed-inside test
```

## Signed distance

```python
from trimesh.proximity import ProximityQuery
pq = ProximityQuery(m)
distances = pq.signed_distance(points)        # < 0 inside, > 0 outside
```

## Transformations

```python
m.apply_translation([0, 0, 1])
m.apply_scale(2.0)
import trimesh.transformations as tf
m.apply_transform(tf.rotation_matrix(angle=0.5, direction=[0, 0, 1]))
```

## Cross-section to 2D path

```python
slice_2d  = m.section(plane_origin=[0,0,0], plane_normal=[0,0,1])
contours  = slice_2d.discrete                  # list of (n, 2) arrays
area_2d   = slice_2d.area
```
