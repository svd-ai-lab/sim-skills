<div align="center">

<img src="assets/banner.svg" alt="sim-skills — teach your agent to drive every engineering tool" width="820">

<br>

**Teach your agent to drive every engineering tool.**

*[`sim-cli`](https://github.com/svd-ai-lab/sim-cli) opens the door.*
*`sim-skills` walks the agent through it.*

<p align="center">
  <a href="#-the-skill-grid"><img src="https://img.shields.io/badge/Skills-growing_library-8b5cf6?style=for-the-badge" alt="Skills library"></a>
  <a href="https://github.com/svd-ai-lab/sim-cli"><img src="https://img.shields.io/badge/Runtime-sim--cli-3b82f6?style=for-the-badge" alt="sim-cli runtime"></a>
  <a href="#-how-an-agent-uses-a-skill"><img src="https://img.shields.io/badge/Format-Anthropic_Skill-22c55e?style=for-the-badge" alt="Anthropic skill format"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-eab308?style=for-the-badge" alt="License"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/category-agent_playbooks-blueviolet" alt="Category">
  <img src="https://img.shields.io/badge/one_folder-per_solver-cbd5e1" alt="One folder per solver">
  <img src="https://img.shields.io/badge/pairs_with-sim--cli-3776AB" alt="Pairs with sim-cli">
  <img src="https://img.shields.io/badge/status-alpha-f97316" alt="Status: alpha">
</p>

[The Skill Grid](#-the-skill-grid) · [Why](#-why-sim-skills) · [How to use](#-how-an-agent-uses-a-skill) · [Conventions](#-cross-skill-conventions) · [Runtime](#-runtime-dependency) · [sim-cli →](https://github.com/svd-ai-lab/sim-cli)

</div>

---

## 🤔 Why sim-skills?

LLM agents already know how to write PyFluent, MATLAB, COMSOL, and OpenFOAM scripts — training data is full of them. What they *don't* have is **operational discipline** for each tool: which inputs are physical decisions vs. operational defaults, what the acceptance criterion actually is, when to stop and ask, which API version's quirks bite where.

Writing the same discipline into every agent prompt from scratch is how teams burn weeks and waste compute. `sim-skills` is the missing library:

- **One folder per solver.** Each folder is a self-contained Anthropic-format skill — `SKILL.md` with YAML frontmatter, plus `reference/`, `workflows/`, `snippets/`, `tests/` as the SKILL.md points to them.
- **Runtime control, not API tutoring.** The skills tell the agent how to drive `sim connect / exec / inspect / disconnect` safely — they assume the agent already knows the solver's own API, and teach it the *operational* layer around that.
- **Cross-skill conventions baked in.** Input classification (Category A/B/C), acceptance-criterion rules, and escalation triggers live in [`CLAUDE.md`](CLAUDE.md) so every skill obeys the same protocol.
- **Paired with [`sim-cli`](https://github.com/svd-ai-lab/sim-cli).** The runtime provides the transport; the skills provide the playbook. Neither works well alone.

> Think of it this way: `sim-cli` is the ignition and the steering wheel. `sim-skills` is the driving school.

---

## 🧭 The Skill Grid

Every skill lives in its own top-level folder. The grid is **open and growing** — add a new skill by dropping a `<solver>/SKILL.md` in and registering it in [`CLAUDE.md`](CLAUDE.md). Current contents of `main`:

| Skill | Domain | Execution model | Phase | What it's for |
|---|---|---|---|---|
| [**sim-cli**](sim-cli/SKILL.md) | *Shared contract* | Both (persistent + one-shot) | Working ✅ | The runtime contract every driver skill depends on — session lifecycle, command surface, input classification, Step-0 version probe, acceptance, escalation. **Load alongside any driver skill below.** |
| [**openfoam-sim**](openfoam/SKILL.md) | CFD (OSS) | Remote `sim serve` on Linux via SSH tunnel | Working ✅ | Meshing, MPI parallel, classifier-based pass/fail on OpenFOAM v2206 |
| [**pybamm-sim**](pybamm/SKILL.md) | Battery modeling | One-shot `sim run --solver pybamm` | Working ✅ | PyBaMM DFN / SPM / SPMe battery models; no separate solver binary — the pybamm package version *is* the solver version. |
| [**calculix-sim**](calculix/SKILL.md) | Static / frequency / thermal FEA | One-shot `ccx -i <file>` | Working ✅ | Open-source Abaqus-dialect `.inp` on Linux. Cantilever tip U2 = −2002 (0.1 % err). |
| [**gmsh-sim**](gmsh/SKILL.md) | Mesh generation | One-shot `gmsh -3 <file.geo>` / Python API | Working ✅ | 2D/3D meshing with CAD import; exports for CalculiX/OpenFOAM/FEniCS/SU2. |
| [**su2-sim**](su2/SKILL.md) | Open-source CFD | One-shot `SU2_CFD <file.cfg>` | Working ✅ | NACA0012 inviscid, RMS[Rho] dropped 3.5 orders. |
| [**lammps-sim**](lammps/SKILL.md) | Molecular dynamics | One-shot `lmp -in <file.in>` | Working ✅ | LJ NVT Nose-Hoover, final T = 1.07 (target 1.5). |
| [**scikit-fem-sim**](scikit_fem/SKILL.md) | Pure-Python FEM | One-shot Python script | Working ✅ | Poisson on unit square, u_max = 0.07345 (0.3 % err). |
| [**elmer-sim**](elmer/SKILL.md) | Multi-physics FEM | One-shot `ElmerSolver <file.sif>` | Working ✅ | CSC-IT `.sif` heat/elasticity/EM/fluid. Steady heat max = 0.07426 (0.8 % err). |
| [**meshio-sim**](meshio/SKILL.md) | Mesh format conversion | One-shot Python script | Working ✅ | 20+ mesh formats, the glue between sim's pre-processors and solvers. |
| [**pyvista-sim**](pyvista/SKILL.md) | Post-processing | One-shot Python script | Working ✅ | Scalar stats, iso-surfaces, area/volume integration, headless PNG. |
| [**pymfem-sim**](pymfem/SKILL.md) | High-order FEM | One-shot Python script | Working ✅ | LLNL MFEM bindings. Poisson u_max = 0.07353 (0.2 % err via UMFPackSolver). |
| [**openseespy-sim**](openseespy/SKILL.md) | Structural / earthquake FEM | One-shot Python script | Working ✅ | PEER's OpenSees. Cantilever tip err 1.3e-12. |
| [**sfepy-sim**](sfepy/SKILL.md) | Pure-Python FEM (weak forms) | One-shot Python script | Working ✅ | Term / Problem API. Poisson 1.3 % err on 8×8 mesh. |
| [**openmdao-sim**](openmdao/SKILL.md) | Multi-disciplinary optimization | One-shot Python script | Working ✅ | NASA MDAO. Sellar coupled MDA y1 = 25.59, y2 = 12.06. |
| [**fipy-sim**](fipy/SKILL.md) | Finite-volume PDE | One-shot Python script | Working ✅ | NIST FVM. 1D steady Poisson err 1.6e-15. |
| [**pymoo-sim**](pymoo/SKILL.md) | Multi-objective optimization | One-shot Python script | Working ✅ | NSGA-II/III, MOEA/D, CMAES. ZDT1 36 Pareto solutions. |
| [**pyomo-sim**](pyomo/SKILL.md) | Optimization modeling | One-shot Python script | Working ✅ | Sandia LP/MIP/NLP. Classic LP obj = 36 via HiGHS. |
| [**simpy-sim**](simpy/SKILL.md) | Discrete-event simulation | One-shot Python script | Working ✅ | Queueing, manufacturing. M/M/1 L err 1.9 %. |
| [**trimesh-sim**](trimesh/SKILL.md) | Triangular-mesh processing | One-shot Python script | Working ✅ | STL/OBJ/PLY, volume/area/inertia. Box V = 24 exact. |
| [**devito-sim**](devito/SKILL.md) | Symbolic FD + JIT C codegen | One-shot Python script | Working ✅ | Imperial College. 2D heat mass conservation 4e-7. |
| [**coolprop-sim**](coolprop/SKILL.md) | Thermo-properties | One-shot Python script | Working ✅ | REFPROP-equivalent. Water @ 1 atm T_sat = 373.124 K. |
| [**scikit-rf-sim**](scikit_rf/SKILL.md) | RF / microwave analysis | One-shot Python script | Working ✅ | Touchstone I/O, S-parameters. Short/open/match S11 = −1/+1/0 exact. |
| [**pandapower-sim**](pandapower/SKILL.md) | Power-system analysis | One-shot Python script | Working ✅ | Fraunhofer IEE. 2-bus PF vm_pu = 0.998, losses 1.4 kW. |
| [**paraview-sim**](paraview/SKILL.md) | Post-processing / visualization | One-shot `pvpython` / `pvbatch` | Working ✅ | Kitware ParaView. 30+ file formats, Clip/Slice/Contour/StreamTracer, headless PNG rendering. |
| [**isaac-sim**](isaac/SKILL.md) | Embodied-AI simulation | One-shot `sim run <script.py> --solver isaac` | Working ✅ | NVIDIA Isaac Sim 4.5 (Omniverse Kit). SimulationApp bootstrap contract, AST lint for import-order, `official_hello_world` + Franka + Replicator + warehouse_sdg snippets. |
| [**newton-sim**](newton/SKILL.md) | GPU physics / embodied AI | Two routes: Route A (recipe JSON) or Route B (`.py` run-script) | Working ✅ | NVIDIA Newton 1.x on Warp. Declarative recipe schema, 6 solver backends (XPBD/VBD/MuJoCo/MPM/Style3D/SemiImplicit), basic_pendulum + robot_g1 + cable_twist E2E workflows. |
| **+ your skill** | — | — | 🛠 | Drop a `<solver>/SKILL.md`, register in `CLAUDE.md`, open a PR |

**Legend** · ✅ Working · 🟡 In progress (phased rollout) · 🛠 Open for contribution

---

## 🎯 How an agent uses a skill

When a task involves a supported solver, the agent follows the same five steps for every skill:

1. **Identify the solver** from the user's request
2. **Read** `<solver>/SKILL.md` — its YAML `description` says exactly when the skill applies, and the body has the required protocol
3. **Follow the protocol**: input validation → connect → execute → verify → report
4. **Reach for supporting files** when SKILL.md tells it to:
   - `reference/` — patterns, templates, API docs
   - `workflows/` — end-to-end example cases
   - `snippets/` — ready-made `sim exec` payloads
   - `skill_tests/` — manual acceptance test cases
5. **Never invent solver-specific defaults** for Category A inputs (physical decisions) — ask the user

The human workflow is even simpler: an engineer points the LLM at `sim-skills`, names the solver, and the agent knows what to do next.

---

## 📏 Cross-skill conventions

These apply to every driver skill in the grid. They live canonically in
the **[`sim-cli/`](sim-cli/SKILL.md)** shared skill — summary here:

| Convention | One-line rule | Full |
|---|---|---|
| **Category A inputs** | Physical decisions (geometry, materials, BCs, acceptance criteria). **Ask the user** if absent. | [input_classification.md](sim-cli/reference/input_classification.md) |
| **Category B inputs** | Operational defaults (processors, ui_mode, smoke-test iterations). May default; must disclose. | [input_classification.md](sim-cli/reference/input_classification.md) |
| **Category C inputs** | File-derivable (cell zones, surface names). Infer via a diagnostic snippet, not from reference examples. | [input_classification.md](sim-cli/reference/input_classification.md) |
| **Acceptance criteria** | `exit_code == 0` is **not** sufficient. Every task needs an outcome-based criterion. | [acceptance.md](sim-cli/reference/acceptance.md) |
| **Step-0 version probe** | Mandatory. `sim inspect session.versions` after connect; pick layered-folder content from the returned profile. | [version_awareness.md](sim-cli/reference/version_awareness.md) |
| **Reference examples ≠ defaults** | Values in `<skill>/reference/examples/` describe a specific published test case. Offer them, never silently adopt them. | [input_classification.md](sim-cli/reference/input_classification.md) |
| **When to stop** | Solver fails to launch, snippet raises or returns `ok=false`, session drifts, acceptance fails → report, don't silently retry. | [escalation.md](sim-cli/reference/escalation.md) |

---

## 🔌 Runtime dependency

These skills are useless without the [`sim-cli`](https://github.com/svd-ai-lab/sim-cli) runtime. The runtime provides:

- `sim connect / exec / inspect / disconnect` for persistent solver sessions
- `sim run` for one-shot scripts
- `sim lint`, `sim logs`, `sim ps` for the operational layer around both

For each solver there is a matching driver, distributed as an out-of-tree plugin package: [`sim-plugin-<solver>`](https://github.com/svd-ai-lab/sim-plugin-index) (browse via `sim plugin list` after installing `sim-runtime`). The skill in this repo is the agent-facing protocol; the plugin is the Python-facing implementation. Neither works well alone.

```bash
# 1. Install the runtime (solver-agnostic core):
uv pip install sim-runtime

# 2. Install the plugin for the solver you want:
sim plugin install <name>          # e.g. sim plugin install pybamm

# 3. Then point your LLM agent at this repo and let it read the SKILL.md files.
```

---

## 📂 Repo layout

```
sim-skills/
├── README.md          this file (human-facing)
├── CLAUDE.md          AI-facing index, protocol, cross-skill conventions
├── LICENSE            Apache-2.0
│
├── openfoam/          OSS solver skill (one example among many)
├── pybamm/            …
├── …/                 one directory per skill — see "Skill Grid" above
│
└── assets/            banner and related graphics
```

Each `<solver>/` directory is self-contained: `SKILL.md` at the top is the agent entry point; the rest (`reference/`, `workflows/`, `snippets/`, `tests/`, `skill_tests/`, `docs/`) is supporting material the SKILL.md links to as needed. Folder shapes vary by skill and by phase.

---

## 🔗 Related projects

- **[`sim-cli`](https://github.com/svd-ai-lab/sim-cli)** — the paired runtime. One CLI, one HTTP protocol, an open driver registry. This repo is its agent-facing twin.
- **[`sim-plugin-index`](https://github.com/svd-ai-lab/sim-plugin-index)** — curated registry of out-of-tree solver plugins (`sim plugin list / install`).

---

## 📄 License

Apache-2.0 — see [LICENSE](LICENSE). Individual skills may ship their own `LICENSE` file (all Apache-2.0 today).
