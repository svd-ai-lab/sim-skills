# basic_pendulum — Route A quickstart

Two-link revolute pendulum with a ground plane, stepped for 20 frames via SolverXPBD on CPU.

## Run

```bash
NEWTON_RECIPE_FRAMES=20 NEWTON_DEVICE=cpu sim run recipe.json --solver newton
```

## Expected envelope

```json
{
  "schema": "sim/newton/v1",
  "data": {
    "solver": "SolverXPBD",
    "num_frames": 20,
    "body_count": 2,
    "joint_count": 2,
    "shape_count": 2,
    "state_path": ".../final.npz"
  }
}
```

## What it exercises

- `add_link` / `add_shape_box` pair
- `add_joint_revolute` with `axis`, `parent_xform` (using axis-angle quaternion), `child_xform`
- `add_articulation` explicit joint list
- `add_ground_plane`
- The default step loop (20 frames × 10 substeps × 60 fps)
- The `sim/newton/v1` envelope with state-array size assertions

## Verified by

`tests/drivers/newton/test_newton_e2e.py::TestBasicPendulumRecipe::test_runs_end_to_end`
