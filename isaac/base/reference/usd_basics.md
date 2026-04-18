# USD basics in Isaac Sim

## World and Scene

```python
from omni.isaac.core import World
world = World(stage_units_in_meters=1.0)
world.scene.add_default_ground_plane()
world.reset()   # must call before stepping
```

`World` wraps a USD stage and a PhysX scene. `World.step(render=False)`
advances physics one frame.

## Adding objects

```python
from omni.isaac.core.objects import DynamicCuboid
import numpy as np

cube = world.scene.add(DynamicCuboid(
    prim_path="/World/Cube",
    name="cube",
    position=np.array([0.0, 0.0, 2.0]),
    size=0.1,
    color=np.array([0.2, 0.6, 1.0]),
))
```

## Stepping

```python
for _ in range(60):
    world.step(render=False)   # skip rendering for speed
```

- `render=False` is much faster in headless — use when you only need physics.
- `render=True` is required if you read camera outputs or use Replicator.

## Reading pose

```python
pos, orient = cube.get_world_pose()  # tuple (np.ndarray(3,), np.ndarray(4,))
print(pos[2])                         # z-height
```

## Stage operations

```python
import omni.usd
stage = omni.usd.get_context().get_stage()
for prim in stage.Traverse():
    print(prim.GetPath())
```
