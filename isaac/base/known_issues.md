# Known issues — Isaac Sim

Findings from E2E runs (Isaac Sim 4.5 on Windows 11 + NVIDIA GPU).

## Installation

- Wheel download is ~15 GB — use `uv` cache to avoid re-download across
  projects (`~/.cache/uv` or `%LocalAppData%\uv\cache` on Windows).
- `--extra-index-url https://pypi.nvidia.com` is mandatory — Isaac is not
  on standard PyPI.
- `--index-strategy unsafe-best-match` is required when both indexes are
  configured, so uv can pick `isaacsim` from NVIDIA pypi while still
  resolving plain deps from PyPI.
- **Python 3.10 strictly required**; 3.11/3.12 wheels do not exist.

## Detection (sim-cli driver)

- `import isaacsim` at runtime triggers `omni.kit_app.check_eula()`, which
  attempts an interactive `input()` prompt. If sim-cli probes with a plain
  `import` **without** `OMNI_KIT_ACCEPT_EULA=YES`, the subprocess hangs or
  exits on EOFError.
- **Fix used**: probe via `importlib.metadata.version('isaacsim')` instead
  of `import isaacsim` — reads package metadata, never bootstraps Kit.

## Runtime

- First launch downloads Nucleus assets (warehouse, Franka USD). Preload
  via `get_assets_root_path()` in an idle-time script if needed for CI.
- `SimulationApp` can only be instantiated **once** per process — no reuse
  in tests that share a pytest session. Mark them `@pytest.mark.serial`.
- `simulation_app.close()` is mandatory; otherwise the Kit subprocess
  leaks threads and may never exit.

## Replicator

- `rep.orchestrator.run()` returns immediately — always follow with
  `wait_until_complete()`, else `close()` may fire before files finish.
- `BasicWriter` writes to `<output_dir>/RenderProduct_*/rgb_*.png`
  (nested subdir per render_product), not flat.
- Colors in distributions must be floats in `[0, 1]`, not `[0, 255]`.

## `isaacsim.core.prims.Articulation` headless bug (4.5.0)

Symptom: `arm.get_joint_positions()` returns `None` in headless runs,
even after `world.reset()` and stepping.

Root cause: `isaacsim.core.prims.Articulation._on_physics_ready` runs
via callback, but `SimulationManager.get_physics_sim_view()._backend`
is `None` in `headless=True` mode until a render pass occurs — and
`render=False` physics-only stepping never triggers that path. Calling
`arm.initialize()` explicitly does not help because `_physics_view` is
created from the same broken simulation view.

Workaround: use the legacy wrapper `omni.isaac.franka.Franka` which
routes through `omni.isaac.core.articulations.ArticulationView` and
does register a working physics view in headless. See the L2 snippet
(`02_franka.py`) for the working pattern. The official 4.5 tutorial
`standalone_examples/tutorials/getting_started_robot.py` requires
`headless=False` and `render=True` to work reliably.

## Additional issues discovered during E2E will be appended here.
