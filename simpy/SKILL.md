---
name: simpy-sim
description: Use when driving SimPy (process-based discrete-event simulation framework in pure Python) via Python scripts — queueing systems, manufacturing lines, network protocols, hospital flow, anything modeled as processes that wait on resources / timeouts / events — through sim runtime one-shot execution.
---

# simpy-sim

You are connected to **SimPy** via sim-cli.

SimPy is the canonical Python DES (discrete-event simulation) framework.
Process-based: simulation logic written as Python generator functions
that `yield` simpy events. Pure Python, no compiled deps.
Pip-installable (`pip install simpy`).

Scripts are plain `.py`:

```python
import simpy

def car(env):
    while True:
        yield env.timeout(5)        # drive 5 time units
        print(f'arrived at {env.now}')

env = simpy.Environment()
env.process(car(env))
env.run(until=20)
```

Same subprocess driver mode as PyBaMM / PyMFEM.

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/workflow.md` | Environment → process generators → resources → run. |
| `base/reference/resources.md` | Resource / Container / Store / PriorityResource. |
| `base/reference/events.md` | timeout / event / process / all_of / any_of. |
| `base/snippets/01_mm1.py` | Verified M/M/1 queue E2E. |
| `base/known_issues.md` | Generators not coroutines, env.now is float, statistical noise. |

## sdk/4/ — SimPy 4.x

- `sdk/4/notes.md` — version-specific surface notes.

---

## Hard constraints

1. **Process functions are generators**, not coroutines. Use `yield env.timeout(...)`,
   `yield env.process(other(env))`, `yield resource.request()`, etc. NOT `await`.
2. **`env.run(until=T)` is the entry point.** Without `until`, it runs
   forever (until no more events are scheduled).
3. **All time arithmetic is in arbitrary units** — pick consistent units
   (seconds, hours, minutes) and document them.
4. **Acceptance != "ran without error"**. Always run for enough time
   that statistics converge (rule of thumb: >= 10000 events) and
   validate against analytical (M/M/1 L = ρ/(1-ρ)) or against a
   simpler reference model.
5. **Seed `random` for reproducibility**: `random.seed(42)`.
6. **Print results as JSON on the last stdout line.**

---

## Required protocol

1. Gather inputs:
   - **Category A:** processes / arrival rate / service distribution /
     resource capacities / acceptance criterion (queue length, throughput,
     utilization, ...).
   - **Category B:** simulation horizon, RNG seed, warm-up period.
2. `sim check simpy`.
3. Write `.py` per `base/reference/workflow.md`.
4. `sim lint script.py`.
5. `sim run script.py --solver simpy`.
6. Validate JSON.
