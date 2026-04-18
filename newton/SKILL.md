---
name: newton-sim
description: "Use when running NVIDIA Newton physics simulations — declarative recipe JSON (Route A) or Python run-script with Warp kernels (Route B), through sim run / sim exec."
---

# Newton Skill

## Identity

| Field | Value |
|---|---|
| Solver | NVIDIA Newton (GPU physics, alpha) |
| Execution | One-shot subprocess: `sim run <recipe.json \| script.py> --solver newton` |
| Session | **No** (v1). A future v2 will add `sim connect --solver newton` for persistent Warp contexts. |
| Engine | Built on [Warp](https://github.com/NVIDIA/warp). CUDA 12 required for GPU execution. CPU also supported. |
| Script language | JSON recipe (`sim/newton/recipe/v1` or legacy `newton-cli/recipe/v1`) **or** Python 3.10+ |
| Input types | `.json` (Route A) or `.py` (Route B) |

## Scope

- **In scope**: Route A declarative recipes (pendulums, robots via USD/MJCF/URDF importers, cloth, softbody, MPM granular); Route B run-scripts for custom Warp kernels, policies, autograd / differentiable sim, IK, selection, sensors.
- **Out of scope (v1)**: Persistent session; live GL viewer interaction (`newton.viewer` picking / UI callbacks); introspection over `sim inspect api.*`.

## Hard constraints

1. **Never import from `newton._src.*`**. Only `newton`, `newton.geometry`, `newton.solvers`, `newton.sim`, `newton.ik`, `newton.sensors`, `newton.usd`, `newton.viewer`, `newton.utils`, `newton.math`, `newton.examples` are public.
2. **Install must include both `newton` and `warp-lang`**. The driver probes `importlib.metadata.version(...)` for both — missing either is reported as `not_installed`.
3. **Recipe schema must be exactly `sim/newton/recipe/v1` or `newton-cli/recipe/v1`**. Anything else is rejected at lint.
4. **Route B scripts dump artifacts to `SIM_ARTIFACT_DIR`** (also aliased as `NEWTON_CLI_ARTIFACT_DIR` for newton-cli script compatibility). Sim rescans this dir after the subprocess exits.
5. **Array-typed params go through file paths**, not inline JSON. Recipe ops that need `wp.array` load from `.npy`/`.npz`.

## Two routes

See `base/reference/two_routes.md` for when to use which.

- **Route A** — declarative recipe JSON. For passive simulation: bodies, joints, shapes, importers, ground planes. 25/58 of newton-cli's canonical examples use this route.
- **Route B** — Python run-script. For custom `@wp.kernel`, torch policies, autograd, IK solvers, selection, sensors. 33/58 examples.

## Quick start

```bash
# Install newton into a dedicated venv (one-time)
uv venv <path> --python 3.12
uv pip install --python <path>/Scripts/python.exe warp-lang newton
setx NEWTON_VENV <path>

# Check availability
sim check newton

# Route A — recipe JSON
sim run path/to/recipe.json --solver newton

# Route B — Python script (uses SIM_ARTIFACT_DIR for outputs)
sim run path/to/script.py --solver newton
```

## Environment variables

| Var | Purpose | Default |
|---|---|---|
| `NEWTON_PYTHON` | Explicit path to newton-capable Python interpreter | — |
| `NEWTON_VENV` | Venv root with newton+warp installed | — |
| `NEWTON_RECIPE_SOLVER` | Solver class name for recipe runs | `SolverXPBD` |
| `NEWTON_RECIPE_FRAMES` | Frame count for recipe runs | `60` |
| `NEWTON_RECIPE_FPS` | Target FPS for step loop | `60` |
| `NEWTON_RECIPE_SUBSTEPS` | Substeps per frame | `10` |
| `NEWTON_DEVICE` | `cpu` or `cuda:0` | Warp default |
| `NEWTON_SOLVER_ARGS` | `;`-separated `key=value` solver kwargs | — |
| `SIM_ARTIFACT_DIR` | Write final state + renders here (Route B) | auto-tempdir |

## Demos

Three TDD-validated workflows under `base/workflows/`:

- `basic_pendulum/` — Route A, `SolverXPBD`, CPU — the hello-world.
- `robot_g1/` — Route A with MJCF importer, `SolverMuJoCo`, GPU — Unitree G1 replicated ×2 on a ground plane.
- `cable_twist/` — Route B, `SolverVBD` via `newton.examples.cable_twist` — exercises the run-script artifact contract.

## See also

- `base/reference/recipe_schema.md` — complete op catalog + arg coercion rules
- `base/reference/solvers.md` — SolverXPBD / VBD / MuJoCo / ImplicitMPM / Style3D / SemiImplicit
- `base/reference/two_routes.md` — Route A vs Route B decision tree
- `base/reference/cli_mapping.md` — newton-cli command → sim command table
- `solver/1_x/notes.md` — Newton 1.x install + CUDA caveats
