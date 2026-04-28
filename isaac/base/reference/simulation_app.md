# SimulationApp — Isaac Sim bootstrap

`SimulationApp` is the entry point for every standalone Isaac script. It boots
Omniverse Kit, loads extensions, and opens a USD stage.

## Minimal

```python
from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless": True})
# only now can you import omni.* / isaacsim.* beyond the SimulationApp class
simulation_app.close()
```

## Config keys (common)

| Key | Type | Default | Use |
|---|---|---|---|
| `headless` | bool | `False` | `True` for servers / CI (no window) |
| `renderer` | str | `RayTracedLighting` | Also `PathTracing` (slower, photoreal) |
| `width` / `height` | int | `1280` / `720` | Viewport size |
| `physics_gpu` | bool | `True` | Set `False` for CPU-only debug |
| `active_gpu` | int | `0` | Multi-GPU: select index |
| `multi_gpu` | bool | `False` | Enable multi-GPU rendering |

## EULA

First launch prompts EULA acceptance. sim-cli auto-sets
`OMNI_KIT_ACCEPT_EULA=YES` so you never see the prompt. To verify:
```bash
echo $OMNI_KIT_ACCEPT_EULA       # unix
echo %OMNI_KIT_ACCEPT_EULA%      # cmd
```

## Teardown

Always call `simulation_app.close()` at the end — otherwise the Kit subprocess
leaks. The driver has a 600 s timeout as a safety net.

## Gotchas

- `from isaacsim import SimulationApp` is the **only** import allowed before
  `SimulationApp(...)` is instantiated. Everything else (including
  `from omni.isaac.core import World`) must come AFTER.
- The instance name `simulation_app` is a convention, not a requirement; but
  the driver's lint check specifically looks for a `SimulationApp(` call and
  any `.close()` call on the resulting object.
