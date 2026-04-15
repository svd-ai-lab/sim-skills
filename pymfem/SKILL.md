---
name: pymfem-sim
description: Use when driving PyMFEM (Python bindings for LLNL's MFEM C++ finite-element library) via Python scripts — H1/H(div)/H(curl) elements, arbitrary polynomial order, static/time/nonlinear PDEs, through sim runtime one-shot execution.
---

# pymfem-sim

You are connected to **PyMFEM** via sim-cli.

MFEM is LLNL's open-source high-performance FEM library (C++, with GPU
support via CUDA/HIP). PyMFEM is the Python binding, distributed as a
self-contained pip wheel including the compiled C++ library.

Two Python modules:
- `import mfem.ser as mfem` — serial (our default)
- `import mfem.par as mfem` — MPI-parallel (requires separate `mfemp` install)

Scripts are plain `.py` that build mesh → FE space → forms → solve.
Same subprocess driver mode as PyBaMM / scikit-fem.

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/workflow.md` | Mesh → FE space → forms → assemble → solve. |
| `base/reference/elements.md` | H1, RT, ND, L2 families + arbitrary order. |
| `base/reference/operators.md` | DiffusionIntegrator, MassIntegrator, VectorFEMassIntegrator, etc. |
| `base/reference/solvers.md` | Direct (UMFPack) vs iterative (CG, GMRES, GSSmoother) + preconditioners. |
| `base/snippets/01_poisson.py` | Verified Poisson E2E. |
| `base/known_issues.md` | Essential BC application, FormLinearSystem unpacking, UMFPackSolver availability. |

## sdk/4/ — PyMFEM 4.8

- `sdk/4/notes.md` — version-specific API + known quirks.

---

## Hard constraints

1. **Essential BCs must be applied via `FormLinearSystem` flow**, not by
   zero-ing rows after assembly. MFEM's idiomatic pattern:
   ```
   a.FormLinearSystem(ess_tdof_list, x, b, A, X, B)
   # solve A X = B
   a.RecoverFEMSolution(X, b, x)
   ```
2. **Acceptance != "ran without error"**. Always verify the computed
   solution against analytical or benchmark values.
3. **MFEM is high-order-friendly** — raising `H1_FECollection(order, dim)`
   order from 1 to 2 typically halves error. Use this for accuracy
   without mesh refinement.
4. **Direct vs iterative solver choice matters**. For small problems
   (< 10k DOFs), `UMFPackSolver` is fast & robust. For larger, use
   PCG with `GSSmoother` or `HypreAMS`/`HypreBoomerAMG` (parallel only).

---

## Required protocol

Gather: PDE, domain, BCs, polynomial order, acceptance criteria.
Write `.py` with standard MFEM workflow. Lint with `sim lint`. Run
with `sim run --solver pymfem`. Validate result JSON.
