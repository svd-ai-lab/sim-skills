"""L3: Replicator SDG — 5 cubes, randomize pose/color, render 20 frames."""
import json
import os
from pathlib import Path

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True, "renderer": "RayTracedLighting"})

import omni.replicator.core as rep

OUT_DIR = Path(os.environ.get("ISAAC_OUT", "_output")).resolve()
OUT_DIR.mkdir(parents=True, exist_ok=True)

with rep.new_layer():
    cubes = rep.create.cube(
        count=5,
        position=rep.distribution.uniform((-1, -1, 0), (1, 1, 0)),
        scale=0.1,
    )
    camera = rep.create.camera(position=(3, 3, 3), look_at=(0, 0, 0))
    render_product = rep.create.render_product(camera, (640, 480))

    with rep.trigger.on_frame(num_frames=20):
        with cubes:
            rep.modify.pose(
                position=rep.distribution.uniform((-1, -1, 0), (1, 1, 1))
            )
            rep.randomizer.color(
                colors=rep.distribution.uniform((0, 0, 0), (1, 1, 1))
            )

    writer = rep.WriterRegistry.get("BasicWriter")
    writer.initialize(
        output_dir=str(OUT_DIR),
        rgb=True,
        bounding_box_2d_tight=True,
    )
    writer.attach([render_product])

rep.orchestrator.run()
rep.orchestrator.wait_until_complete()

pngs = sorted(OUT_DIR.rglob("rgb_*.png"))
simulation_app.close()

print(json.dumps({
    "level": "L3",
    "output_dir": str(OUT_DIR),
    "frames_rendered": len(pngs),
    "first_image": str(pngs[0]) if pngs else None,
}))
