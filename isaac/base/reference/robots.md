# Robots — ArticulationView

## Franka example

```python
from omni.isaac.franka import Franka

franka = world.scene.add(Franka(prim_path="/World/Franka", name="franka"))
world.reset()

q = franka.get_joint_positions()         # shape (1, 9)  — 7 arm + 2 gripper
franka.set_joint_positions(q + 0.01)      # small nudge
```

The first dimension (size 1) is the number of instances; Franka defaults
to a single instance.

## Generic ArticulationView

For multiple articulations of the same kind, use `ArticulationView` with a
glob pattern:

```python
from omni.isaac.core.articulations import ArticulationView

view = ArticulationView(prim_paths_expr="/World/Robot_*")
view.initialize()
qs = view.get_joint_positions()   # shape (N, num_joints)
```

## Importing URDF

```python
from omni.isaac.urdf import _urdf

urdf_interface = _urdf.acquire_urdf_interface()
import_config = _urdf.ImportConfig()
import_config.fix_base = True
urdf_interface.parse_urdf("/path/to/robot.urdf", import_config)
urdf_interface.import_robot(...)
```

## Controllers

- `ArticulationController.apply_action(ArticulationAction(joint_positions=...))`
- For velocity control use `joint_velocities=`
- For torque / effort use `joint_efforts=` (requires physics backend support)
