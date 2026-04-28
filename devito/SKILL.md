---
name: devito-sim
description: Use when driving Devito (symbolic finite-difference DSL with JIT C codegen, originally for seismic imaging at Imperial College) via Python scripts — wave / heat / acoustic / elastic PDEs on regular grids with high-order stencils, automatic vectorization & OpenMP through codegen, through sim runtime one-shot execution.
---

# devito-sim

You are connected to **Devito** via sim-cli.

Devito generates and JIT-compiles optimized C kernels from a symbolic
finite-difference description (built on SymPy). Pip-installable
(`pip install devito`); requires a system C compiler (gcc/clang)
present on PATH.

Scripts are plain `.py`:

```python
from devito import Grid, TimeFunction, Eq, solve, Operator
grid = Grid(shape=(100, 100), extent=(1.0, 1.0))
u = TimeFunction(name='u', grid=grid, time_order=1, space_order=2)
eq = Eq(u.dt, 0.1*(u.dx2 + u.dy2))            # diffusion
op = Operator([Eq(u.forward, solve(eq, u.forward))])
op.apply(time_M=100, dt=0.001)
```

Same subprocess driver mode as PyBaMM / PyMFEM.

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/workflow.md` | Grid → Function → Eq → Operator → apply. |
| `base/reference/derivatives.md` | `.dt`, `.dx`, `.dx2`, `.laplace`, mixed derivatives. |
| `base/reference/operators.md` | `solve()`, `Operator()`, time_M / space iteration limits. |
| `base/snippets/01_diffusion.py` | Verified 2D heat-diffusion E2E. |
| `base/known_issues.md` | C compiler dep, time_order vs space_order, codegen cache. |

## sdk/4/ — Devito 4.x

- `sdk/4/notes.md` — version-specific surface notes.

---

## Hard constraints

1. **Devito requires a C compiler on PATH** (gcc, clang, or icc). The
   driver detects Devito Python module; runtime compile failures show
   up at first `op.apply(...)` call.
2. **`Function` for static fields, `TimeFunction` for time-dependent**.
   `TimeFunction(time_order=N)` allocates N+1 time slots (current +
   N history) cyclically.
3. **CFL stability**: explicit schemes need `dt ≤ C * dx² / α` (diffusion)
   or `dt ≤ dx / v` (advection / wave). Pick conservatively.
4. **Acceptance != "ran without error"**. Validate against:
   - mass / energy conservation (closed BC: sum should be invariant)
   - analytical (e.g. Gaussian diffusion peak decay, plane wave amplitude)
   - peak position (advection: should move v*t)
5. **Print results as JSON on the last stdout line.** Cast numpy floats:
   `float(u.data[-1].max())`.

---

## Required protocol

1. Gather inputs:
   - **Category A:** PDE, domain shape & extent, IC/BCs, time span,
     stencil order, acceptance.
   - **Category B:** dt, OpenMP threads (env var `DEVITO_LANGUAGE=openmp`
     and `OMP_NUM_THREADS`), codegen cache dir.
2. `sim check devito`.
3. Write `.py` per `base/reference/workflow.md`.
4. `sim lint script.py`.
5. `sim run script.py --solver devito`.
6. Validate JSON.
