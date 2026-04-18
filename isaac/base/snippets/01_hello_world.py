"""L1: Headless Isaac Sim — drop a cube, step 60 frames, print JSON."""
import json

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True})

from omni.isaac.core import World
from omni.isaac.core.objects import DynamicCuboid
import numpy as np

world = World(stage_units_in_meters=1.0)
cube = world.scene.add(
    DynamicCuboid(
        prim_path="/World/Cube",
        name="cube",
        position=np.array([0.0, 0.0, 2.0]),
        size=0.1,
        color=np.array([0.2, 0.6, 1.0]),
    )
)
world.scene.add_default_ground_plane()
world.reset()

start_z = float(cube.get_world_pose()[0][2])
for _ in range(60):
    world.step(render=False)
end_z = float(cube.get_world_pose()[0][2])

simulation_app.close()

print(json.dumps({
    "level": "L1",
    "start_z_m": start_z,
    "end_z_m": end_z,
    "delta_z_m": start_z - end_z,
    "frames": 60,
}))
