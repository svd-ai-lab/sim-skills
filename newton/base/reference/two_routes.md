# Two routes — when to use which

Newton exposes two complementary ways to drive a simulation through `sim`.

## Route A — declarative recipe JSON

**Use when:** The simulation is a passive time-evolution of a scene with fixed topology. No per-step user code.

- Input: `<name>.json` with `"schema": "sim/newton/recipe/v1"`
- Every op is a `ModelBuilder` method call (or a small set of interpreter primitives)
- Solver / frames / fps / substeps / device are controlled by env vars (driver-level), not by the recipe
- Agent-friendly: an LLM emits JSON, not code
- No per-step custom kernels

```bash
sim run scene.json --solver newton
```

**Coverage in the canonical 58 newton-cli examples:** 25/58 (43%).

## Route B — Python run-script

**Use when:** You need per-step Python. Any of:

- Custom `@wp.kernel` that applies forces/torques at each substep
- Torch / JAX policy producing control
- Autograd / differentiable sim (loss + `wp.Tape`)
- IK solver loop (`newton.ik`)
- Selection / masking that depends on per-step state
- Sensor readout (`newton.sensors`)

Write a plain Python file; sim runs it with `SIM_ARTIFACT_DIR` in env. Dump `final.npz`, plots, logs to that dir — they'll be listed as artifacts in the envelope.

```bash
sim run my_sim.py --solver newton
```

The script has full access to `newton`, `warp`, `numpy`, etc. via the newton venv.

**Coverage in the canonical 58 newton-cli examples:** 33/58 (57%).

## Decision tree

```
      Need per-step Python?
       ┌─────┴─────┐
      no           yes
       │            │
   Route A      Route B
       │            │
  recipe.json   script.py
```

If you're unsure: start with Route A. Switch to Route B the moment you need a `@wp.kernel` or per-step control.

## Capability gap

There is none. Everything Route A can express, Route B can also express (plus more). Route A is a convenience shortcut for the common "build, run, save" pattern.
