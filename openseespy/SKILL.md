---
name: openseespy-sim
description: Use when driving OpenSeesPy (PEER's structural earthquake-engineering FEM framework) via Python scripts — elastic/inelastic beams, fiber sections, nonlinear pushover, time-history seismic analysis, eigenvalue/modal — through sim runtime one-shot execution.
---

# openseespy-sim

You are connected to **OpenSeesPy** via sim-cli.

OpenSees (Open System for Earthquake Engineering Simulation) is the
structural / geotechnical FEM framework developed at PEER (UC Berkeley).
OpenSeesPy is the Python interpreter wrapper, distributed as pip wheels:
- `openseespy` — pure Python facade
- `openseespylinux` / `openseespywin` / `openseespymac` — compiled core

Scripts are plain `.py`:

```python
import openseespy.opensees as ops
ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)
ops.node(...); ops.element(...)
ops.timeSeries(...); ops.pattern(...); ops.load(...)
ops.system(...); ops.numberer(...); ops.constraints(...)
ops.integrator(...); ops.algorithm(...); ops.analysis(...)
ops.analyze(N)
disp = ops.nodeDisp(node, dof)
```

Same subprocess driver mode as PyBaMM / PyMFEM / scikit-fem.

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/workflow.md` | Standard analysis workflow — model → loads → analysis options → analyze → query. |
| `base/reference/model_dim.md` | `ndm`/`ndf` choices and their DOF semantics (1D/2D/3D). |
| `base/reference/elements.md` | truss / elasticBeamColumn / forceBeamColumn / quad / brick. |
| `base/reference/analysis.md` | Static / Transient / EigenAnalysis; system/numberer/algorithm/integrator combos. |
| `base/snippets/01_cantilever.py` | Verified elastic cantilever tip-deflection E2E. |
| `base/known_issues.md` | `Process 0 Terminating` stderr, `wipe()` between runs, fix DOF-count consistency. |

## sdk/3/ — OpenSeesPy 3.x

- `sdk/3/notes.md` — version-specific API surface notes.

---

## Hard constraints

1. **Always call `ops.wipe()` first.** OpenSees holds global state across
   model commands; not wiping leaks nodes / elements between runs.
2. **`ndf` must match every `node`/`fix`/`load` call.** A 2D Euler-Bernoulli
   beam needs `ndm=2, ndf=3` (ux, uy, rotz). A 2D truss needs `ndm=2, ndf=2`
   (ux, uy). Mismatched DOF counts silently corrupt boundary conditions.
3. **Static analysis requires the full chain**:
   `system → numberer → constraints → integrator → algorithm → analysis`.
   Skipping any of these gives "analysis object not constructed" errors.
4. **Acceptance != "ran without error"**. `ops.analyze(N)` returns 0 on
   success, non-zero on failure — but always also validate against an
   analytical/benchmark result (tip deflection, period, mode shape, ...).
5. **Do not parse stderr for failure detection.** OpenSees prints
   `Process 0 Terminating` to stderr on every interpreter exit, even on
   success. Use the `analyze()` return code and JSON output instead.

---

## Required protocol

1. Gather inputs:
   - **Category A (must ask):** geometry, materials, boundary conditions,
     loading, acceptance criterion (e.g. "tip deflection within 1% of
     analytical").
   - **Category B (may default, must disclose):** mesh density, integration
     rule, solver type (`BandSPD`, `UmfPack`, ...).
   - **Category C (file-derivable):** none — OpenSeesPy is pure code.
2. Run `sim check openseespy` to confirm the wheel is importable.
3. Write `.py` script following the workflow in `base/reference/workflow.md`.
4. `sim lint script.py` to catch missing import / syntax / no-usage warnings.
5. `sim run script.py --solver openseespy` for one-shot execution.
6. Parse the last JSON line of stdout for results; validate against the
   acceptance criterion.
