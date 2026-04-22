# robot_g1 — Route A with USD importer + replicate

Two Unitree G1 humanoids on a ground plane, driven by SolverMuJoCo.

## Prerequisite: G1 asset download

The recipe references a cached USD path. Newton fetches it via `newton.utils.download_asset("unitree_g1")` on first use; run once in the newton venv:

```bash
"<NEWTON_VENV>/Scripts/python.exe" -c "import newton.utils; print(newton.utils.download_asset('unitree_g1'))"
```

The printed path should match the hardcoded `source` in `recipe.json` — if your cache prefix differs, edit `source` to match.

## Run

```bash
NEWTON_RECIPE_SOLVER=SolverMuJoCo \
NEWTON_RECIPE_FRAMES=10 \
NEWTON_RECIPE_FPS=60 \
NEWTON_RECIPE_SUBSTEPS=2 \
sim run recipe.json --solver newton
```

## Expected envelope (excerpt)

```json
{
  "schema": "sim/newton/v1",
  "data": {
    "solver": "SolverMuJoCo",
    "num_frames": 10,
    "body_count": 34,
    "joint_count": 30,
    "shape_count": 10,
    "state_path": ".../final.npz"
  }
}
```

(Body/joint counts: 2 × 15 bodies per G1 + 2 extra articulation links after `collapse_fixed_joints`, 2 × 15 joints.)

## What it exercises

- `replicate` op with an **inline sub-recipe** (no separate builder file)
- `register_mujoco_custom_attributes` — must precede `add_usd` so MuJoCo custom attrs in the USDA are captured
- `set_default_joint_cfg` / `set_default_shape_cfg` to configure contact stiffness + friction
- `add_usd` with `collapse_fixed_joints=true`, `enable_self_collisions=false`, `skip_mesh_approximation=true`
- `set_builder_array` with `fill` + `range` for PID gains on non-root joints
- `SolverMuJoCo` (articulated-robot-native step)

## Verified by

`tests/drivers/newton/test_newton_e2e.py::TestRobotG1Recipe::test_runs_end_to_end`
