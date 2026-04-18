# Isaac Sim 4.5 SDK notes

## Namespace migration

Isaac 4.5 began migrating core APIs from `omni.isaac.*` to `isaacsim.*`:

| Legacy (≤4.2) | 4.5 preferred |
|---|---|
| `from omni.isaac.kit import SimulationApp` | `from isaacsim import SimulationApp` |
| `omni.isaac.core.World` | still valid; may move to `isaacsim.core.api.World` |
| `omni.isaac.core.objects.DynamicCuboid` | still valid |
| `omni.isaac.franka.Franka` | still valid |
| `omni.isaac.core.articulations.ArticulationView` | still valid |

When in doubt, try the `isaacsim.*` path first, fall back to `omni.isaac.*`.

## New in 4.5

- Async-friendly `rep.orchestrator.run_async()`
- Tighter PhysX integration (fewer stepping quirks)
- RTX renderer default for headless (falls back to OSMesa if no GPU)
- `omniverse-kit` bumped to 106.5.x

## Python requirement

- Wheel built for CPython 3.10 only.
- `importlib.metadata.version('isaacsim')` returns `"4.5.0"` for release
  4.5.0 (what sim-cli pins against).

## Key bundled packages (4.5.0 snapshot)

- `omniverse-kit` 106.5.0
- `torch` 2.11
- `numpy` 1.26
- `scipy` 1.15
- `opencv-python` 4.11
- `omni-pxr-usd` (bundled USD)
