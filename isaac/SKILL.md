---
name: isaac-sim
description: Use for NVIDIA Isaac Sim simulations — USD scene setup, PhysX stepping, robot articulation, and Replicator synthetic-data generation (SDG). Scripts run one-shot via isaacsim pip wheel in an isolated Python 3.10 venv. Every script must bootstrap `SimulationApp({...})` before any `omni.*` or `isaacsim.*` imports.
---

# isaac-sim

You are connected to **NVIDIA Isaac Sim** via sim-cli.

Isaac Sim is NVIDIA Omniverse-Kit's embodied-AI simulator (USD + PhysX + RTX).
It is sim's solver of choice for **synthetic-data generation** (Replicator) and
**robot learning** scenes.

Scripts are plain Python. Every script MUST start by constructing
`SimulationApp(...)` before any `omni.*` / `isaacsim.*` imports. Execution is
one-shot via `sim run script.py --solver isaac` (v1; v2 will add session).

---

## Identity

| Field | Value |
|---|---|
| Solver | NVIDIA Isaac Sim |
| Execution mode | One-shot subprocess (`<venv>/python.exe script.py`) |
| Session type | None (v1) |
| SDK | `isaacsim` pip wheel (NVIDIA pypi) |
| Script language | Python 3.10 |
| Input | `.py` scripts |
| Output | JSON on stdout (last line), PNG/USD files, annotations |

---

## Install

Isaac Sim ships as a large (~15 GB) pip wheel that must live in its own
Python 3.10 venv (separate from sim's main Python).

```bash
uv venv "<path/to/isaac-venv>" --python 3.10
uv pip install --python "<path/to/isaac-venv>/Scripts/python.exe" \
    "isaacsim[all]" --extra-index-url https://pypi.nvidia.com \
    --index-strategy unsafe-best-match

# Windows persistent:
setx ISAAC_VENV "<path/to/isaac-venv>"
# Unix:
export ISAAC_VENV="<path/to/isaac-venv>"
```

Verify with `sim check isaac` — expected `status: ok, version: 4.5`.

---

## Hard constraints

1. **`SimulationApp` first.** Every script must:
   ```python
   from isaacsim import SimulationApp
   simulation_app = SimulationApp({"headless": True})
   # only AFTER this line may you import omni.* or isaacsim.* beyond the app
   ```
   Linter errors if `SimulationApp()` is missing; warns if import order is wrong.

2. **One process per script.** `SimulationApp` cannot be instantiated twice.
   Use subprocess boundaries for multi-scene work.

3. **Close before exit.** `simulation_app.close()` at end, else process hangs.

4. **Replicator needs `rep.orchestrator.run()`.** Defining the graph is not
   enough — you must trigger execution.

5. **`OMNI_KIT_ACCEPT_EULA=YES`** is injected by sim automatically — no user action.

6. **JSON on last stdout line.** All snippets must `print(json.dumps({...}))`
   as the final output for `driver.parse_output()` to extract.

7. **Python 3.10 only.** Wheel will refuse to import on 3.11/3.12.

---

## File index

### base/ — always relevant

| Path | Content |
|---|---|
| `base/reference/simulation_app.md` | Startup flags, headless, renderer, EULA |
| `base/reference/usd_basics.md` | Stage/Prim/Xform, World, DynamicCuboid, step loop |
| `base/reference/replicator.md` | `omni.replicator.core`: distributions, triggers, writers |
| `base/reference/robots.md` | Franka, ArticulationView, joint read/write |
| `base/snippets/01_hello_world.py` | L1 — drop cube, report ΔZ |
| `base/snippets/02_franka.py` | L2 — load Franka, read joints |
| `base/snippets/03_replicator_cubes.py` | L3 — SDG, 20 frames + bbox |
| `base/snippets/04_warehouse_sdg.py` | L4 — warehouse scene SDG |
| `base/known_issues.md` | Failure modes discovered during E2E |

### sdk/ — version-specific

| Path | Content |
|---|---|
| `sdk/4_5/notes.md` | Isaac Sim 4.5 API, namespace migration notes |

### solver/ — solver-version notes

| Path | Content |
|---|---|
| `solver/4_5/notes.md` | 4.5 renderer / Replicator quirks |

---

## Required protocol

### Step 0 — Version check

```bash
sim check isaac
```

### Step 1 — Input validation

| Input | Category | Action |
|---|---|---|
| Script path | A | Must be provided |
| Output directory | A | Must ask (`ISAAC_OUT` env or CLI arg) |
| Frame count / dataset size | A | Must ask |
| Renderer (`RayTracedLighting` / `PathTracing`) | B | Default `RayTracedLighting`, disclose |
| Image resolution | B | Default 640×480, disclose |

### Step 2 — Bootstrap

```python
from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless": True})
```

### Step 3 — Build scene / pipeline

### Step 4 — Step or run Replicator

### Step 5 — `simulation_app.close()` + `print(json.dumps({...}))`

### Step 6 — Acceptance validation

Check parsed JSON against user-specified criteria. `exit_code == 0` alone
is not sufficient.
