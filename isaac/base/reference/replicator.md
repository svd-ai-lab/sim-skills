# Replicator SDG — `omni.replicator.core`

Replicator is a graph-based synthetic-data engine. You declare a graph, attach
a writer, then call `orchestrator.run()` → `wait_until_complete()`.

## Minimal SDG

```python
import omni.replicator.core as rep

with rep.new_layer():
    cubes = rep.create.cube(count=5, scale=0.1)
    camera = rep.create.camera(position=(3, 3, 3), look_at=(0, 0, 0))
    rp = rep.create.render_product(camera, (640, 480))

    with rep.trigger.on_frame(num_frames=20):
        with cubes:
            rep.modify.pose(position=rep.distribution.uniform((-1, -1, 0), (1, 1, 1)))

    w = rep.WriterRegistry.get("BasicWriter")
    w.initialize(output_dir="_out", rgb=True, bounding_box_2d_tight=True)
    w.attach([rp])

rep.orchestrator.run()
rep.orchestrator.wait_until_complete()
```

## Writers

- `BasicWriter` — RGB, depth, bbox (2D tight/loose), semantic segmentation
- `KittiWriter` — KITTI autonomous-driving format
- `YoloWriter` — YOLO detection format
- Custom writers: subclass `rep.Writer`, override `write(data)`

## Distributions

| Distribution | Signature | Example |
|---|---|---|
| `rep.distribution.uniform(low, high)` | scalars or tuples | `uniform((0, 0, 0), (1, 1, 1))` |
| `rep.distribution.normal(mean, std)` | scalars | `normal(0.0, 0.1)` |
| `rep.distribution.choice([...])` | list | `choice(["red", "blue"])` |
| `rep.distribution.sequence([...])` | list | frame-by-frame iteration |

## Triggers

- `rep.trigger.on_frame(num_frames=N)` — fire every frame for N frames
- `rep.trigger.on_time(interval=0.1)` — fire every `interval` seconds
- `rep.trigger.on_custom_event(event_name=...)` — manual

## Common pitfalls

- **Must call `orchestrator.run()`** — graph definition alone writes nothing.
- **Must call `wait_until_complete()`** — without it, `close()` may fire before files finish writing.
- **Colors are floats in `[0, 1]`**, not `[0, 255]`.
- **BasicWriter writes to nested dirs**: `<output_dir>/RenderProduct_*/rgb_*.png`.
- **Camera must be inside `new_layer()`** context, otherwise graph is empty.
