---
name: scikit-fem-sim
description: Use when driving scikit-fem (pure-Python finite element library) via Python scripts — weak form assembly, function spaces, boundary conditions, linear/nonlinear PDE solves, through sim runtime one-shot execution.
---

# scikit-fem-sim

You are connected to **scikit-fem** via sim-cli.

scikit-fem is a lightweight, pure-Python FEM library. No separate
solver binary — the "solver" IS the `skfem` pip package. Scripts are
plain `.py` files that `import skfem` and use the library to:

1. Build a mesh (`MeshTri`, `MeshQuad`, `MeshTet`, etc.)
2. Pick a function space (`ElementTriP1`, `ElementTetP2`, etc.)
3. Define weak forms with `@BilinearForm` / `@LinearForm`
4. Assemble matrices with `asm()`
5. Apply Dirichlet BCs with `condense()`
6. Solve with `solve()`

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/api_overview.md` | Mesh classes, Element types, Basis, BilinearForm/LinearForm, asm, solve. |
| `base/reference/weak_forms.md` | Translating PDEs into scikit-fem's weak form decorators. |
| `base/reference/boundary_conditions.md` | Dirichlet via `condense`, Neumann via `facet_basis`. |
| `base/snippets/01_poisson_unit_square.py` | Verified Poisson E2E (u_max ≈ 0.0737). |
| `base/known_issues.md` | Pure-Python perf limits, meshio for external meshes. |

## sdk/12/ — scikit-fem 12.x specifics

- `sdk/12/notes.md` — API notes for 12.x line.

---

## Hard constraints

1. **scikit-fem is pure Python** — no MPI, no GPU. Performance ceiling is
   ~100k DOFs for comfortable run times. For larger problems, consider
   FEniCS/dolfinx.
2. **Always decorate weak forms** with `@BilinearForm` / `@LinearForm`.
   Untagged functions are not recognized by `asm()`.
3. **`condense(A, b, D=...)` returns reduced system** — you must pass
   `*condense(...)` to `solve()` (unpacks tuple).
4. **Acceptance != "ran without exception".** Validate numerical
   solution against analytical / benchmark values where possible.
5. **Mesh refinement is exponential** — `.refined(N)` produces 4^N
   elements (2D) or 8^N (3D). Start small.

---

## Required protocol

After `sim check scikit_fem`: gather Category A inputs (PDE, domain,
BCs, acceptance criteria). Write `.py` script. Lint with `sim lint`.
Run with `sim run --solver scikit_fem`. Validate numerical solution
against reference values.
