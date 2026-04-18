# cable_twist — Route B (run-script) via newton.examples

A Warp cable (VBD solver) twisted by a custom per-step kernel. The recipe interpreter can't express the twist kernel, so this goes through Route B.

## How it works

`script.py` rewrites `sys.argv` to drive `newton.examples.cable_twist` with `--viewer null --test --num-frames 20`, then monkey-patches `newton.examples.run` to capture the `Example` instance so we can dump final state into `SIM_ARTIFACT_DIR`.

## Run

```bash
sim run script.py --solver newton
```

No extra env vars — the script hardcodes `num_frames=20` to keep wall-time under a few seconds.

## Expected envelope (excerpt)

```json
{
  "schema": "sim/newton/v1",
  "data": {
    "artifact_dir": ".../sim_newton_.../",
    "artifacts": [
      {"path": ".../final.npz", "kind": "state", "size": 8192}
    ],
    "duration_s": 2.95
  }
}
```

Route B envelopes don't carry `solver` / `num_frames` (those are internal to the script) unless the script drops a `meta.json` alongside `final.npz` — then those fields get merged in.

## What it exercises

- Route B subprocess launch + PATH injection for `sim.drivers.newton._entry`
- `newton.examples.main()` execution under `--test` (example's own `test_final()` runs and would `sys.exit(1)` on failure)
- Artifact auto-collection: the driver re-scans `SIM_ARTIFACT_DIR` after exit
- `final.npz` round-trip round-tripping body/joint/particle arrays

## Verified by

`tests/drivers/newton/test_newton_e2e.py::TestCableTwistRunScript::test_runs_end_to_end`
