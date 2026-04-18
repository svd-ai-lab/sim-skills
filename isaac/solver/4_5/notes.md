# Isaac Sim 4.5 solver notes

## PhysX

- Default scene uses CPU PhysX. For GPU PhysX:
  ```python
  world = World(
      physics_prim_path="/World/physicsScene",
      backend="torch",
      device="cuda",
  )
  ```
- Contact / restitution params on
  `DynamicCuboid.get_applied_physics_material()`.

## Renderer

- `RayTracedLighting` is default. Fast, decent quality, good for SDG.
- `PathTracing` is photoreal but 5-10× slower. Use for final SDG passes.
- Headless renderer works via GPU if available; falls back gracefully
  to software OSMesa on CPU-only hosts (very slow).

## Headless

- `"headless": True` required on servers / CI.
- Without a display, use `"renderer": "RayTracedLighting"` + GPU.
- `nvidia-smi` should list the GPU; driver ≥ 550 recommended.

## Typical boot time

- Cold boot (first SimulationApp of a process): ~30 s
- Subsequent scene loads (same process): ~2-5 s (but see constraint below)

## Constraint: one SimulationApp per process

`SimulationApp` cannot be instantiated twice. Sim-cli v1 is strictly
one-shot — each `sim run script.py --solver isaac` invocation is a fresh
subprocess with a fresh Kit.
