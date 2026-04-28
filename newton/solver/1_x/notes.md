# Newton 1.x notes

Newton is in alpha. These notes cover what's verified against 1.2.0.dev0 + warp-lang 1.12.1.

## Install

Newton is not on PyPI under its upstream form; the sanctioned install uses the user's own venv with path-dep to the upstream tree:

```bash
# clone newton alongside newton-cli
git clone https://github.com/newton-physics/newton <path>/newton
git clone https://github.com/Terry-cyx/newton-cli <path>/newton-cli

# venv + install
uv venv <path>/newton-cli/.venv --python 3.12
uv pip install -e <path>/newton-cli          # newton-cli itself
uv pip install -e <path>/newton[importers,sim]   # newton + optional deps

# point sim at it
setx NEWTON_VENV <path>/newton-cli/.venv
```

Alternative (skip newton-cli): just install `warp-lang` + `newton` into any venv.

## Python version

- **3.10, 3.11, 3.12** — known-good
- **3.13** — not recommended on Windows; CUDA torch wheels for Py3.13 are not consistently available via `uv` (this blocks 3/58 newton-cli examples that need `torch-cu12`).

## CUDA

- **CUDA 12** required for GPU execution (Warp's dependency).
- CPU execution works on any platform but is 10-100× slower for anything over a few bodies.
- For examples that don't need GPU, set `NEWTON_DEVICE=cpu` — all of the basic_* workflows pass on CPU.

## Known limitations (1.2.x)

1. **`newton.viewer` picking / UI callbacks don't run headlessly** — 2 newton-cli examples (`contacts_rj45_plug`, `replay_viewer`) can't be reproduced via Route B.
2. **`SolverImplicitMPM` Config fields are unstable** — some fields renamed between 1.1 and 1.2. When passing `NEWTON_SOLVER_ARGS` to MPM, check the Config class on the installed version.
3. **`torch-cu12` wheels flaky on 3.13/Windows** — examples with torch policies skip there.
4. **USD asset cache path** is platform-specific: on Windows it's under `%LOCALAPPDATA%\newton-physics\newton\Cache\`. If you move machines, re-run `newton.utils.download_asset(...)` before running `robot_g1`.

## Upgrade path

When Newton stabilizes (≥2.0), add a new profile block to `src/sim/drivers/newton/compatibility.yaml`:

```yaml
- name: newton_2_x
  solver_versions: ["2.0", "2.1"]
  active_sdk_layer: "2_x"
  active_solver_layer: "2_x"
```

Then add a sibling layer dir under `solver/2_x/` with version-specific notes.
