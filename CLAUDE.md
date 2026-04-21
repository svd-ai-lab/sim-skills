# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code under `sim-skills/`.

## What is this directory?

`sim-skills/` is a collection of agent skills for the [`sim`](../sim-cli/) simulation runtime. It contains two kinds of skill:

- **[`sim-cli/`](sim-cli/SKILL.md)** — the shared runtime-contract skill. Owns session lifecycle, command surface, input classification, Step-0 version awareness, acceptance, and escalation. Load alongside any driver skill.
- **Per-solver skills** (`abaqus/`, `ansa/`, `cfx/`, `comsol/`, `flotherm/`, `fluent/`, `lsdyna/`, `mapdl/`, `matlab/`, `mechanical/`, `openfoam/`, `pybamm/`, `starccm/`, `workbench/`, …). Each is one Anthropic-format skill that layers solver-specific rules on top of the shared contract.

```
<solver>/
  SKILL.md         ← required, with YAML frontmatter (name + description)
  <supporting files: reference/, workflows/, snippets/, tests/, docs/, ...>
```

The skills tell an LLM agent **how to drive a given solver through `sim`** — input validation, connect, execute snippets / scripts, verify acceptance, classify success/failure, recover from common errors. They are *runtime control* skills, not general solver tutorials.

## How to use these skills

When a task involves any supported solver:

1. **Load [`sim-cli/SKILL.md`](sim-cli/SKILL.md)** for the shared runtime contract.
2. Identify the solver from the user's request.
3. Read `<solver>/SKILL.md` — its YAML `description` field describes exactly when it applies, and the body has the solver-specific overlay on top of the sim-cli contract.
4. Follow the protocol step by step (input validation → connect / run → execute → verify → report).
5. Reach for supporting files when SKILL.md instructs: `reference/` for patterns and templates, `workflows/` for end-to-end examples, `snippets/` for ready-made `sim exec` payloads, `skill_tests/` for acceptance test cases.
6. **Never invent solver-specific defaults for Category A (physical-decision) inputs** — ask the user.

## Skills

The shared-contract skill ([`sim-cli/`](sim-cli/SKILL.md)) is listed
above. The per-solver skills follow.



| Directory | Skill name | Use when |
|---|---|---|
| `abaqus/` | `abaqus-sim` | Running Dassault Systemes SIMULIA Abaqus via `.inp` input decks or Abaqus/CAE Python scripts — static/dynamic/thermal FEA through sim one-shot execution. |
| `ansa/` | `ansa-sim` | Running BETA CAE ANSA v25 pre-processor scripts in headless batch (Phase 1; no persistent session, no GUI) |
| `comsol/` | `comsol-sim` | Driving COMSOL Multiphysics via the JPype Java API, with optional human GUI oversight |
| `flotherm/` | `flotherm-sim` | Running Simcenter Flotherm 2504 thermal `.pack` cases via GUI + Win32 FloSCRIPT playback (Phase A) |
| `fluent/` | `fluent-sim` | Driving an Ansys Fluent meshing or solver session via PyFluent 0.38 — incremental snippets or single-file workflows |
| `matlab/` | `matlab-sim` | Running MATLAB `.m` scripts one-shot via `sim run --solver matlab` (v0); persistent sessions planned for v1 |
| `mechanical/` | `mechanical-sim` | Driving Ansys Mechanical via PyMechanical — BCs, loads, solver execution, result extraction. Owns cells 4-6 of Static Structural. Observation commands tightly coupled with live GUI window (`batch=False`). |
| `openfoam/` | `openfoam-sim` | Running OpenFOAM v2206 cases through `sim serve` on a Linux box via SSH tunnel — meshing, MPI parallel, classifier-based pass/fail |
| `pybamm/` | `pybamm-sim` | Running PyBaMM battery models (DFN / SPM / SPMe) one-shot via `sim run --solver pybamm` — pure Python, no separate solver binary; the pybamm package version *is* the solver version. |
| `starccm/` | `starccm-sim` | Running Simcenter STAR-CCM+ 2602 via Java macros in batch mode — CFD/multiphysics geometry creation, mesh generation, solver execution, result extraction. |
| `workbench/` | `workbench-sim` | Driving Ansys Workbench via PyWorkbench SDK — project creation, analysis systems, IronPython journals, sub-solver integration (PyMechanical/PyFluent). Owns cells 1-3 of Static Structural. |
| `cfx/` | `cfx-sim` | Running Ansys CFX simulations via CCL definition files and cfx5solve batch execution — turbomachinery and general-purpose CFD with cfx5post visualization. |
| `lsdyna/` | `lsdyna-sim` | Running Ansys LS-DYNA explicit/implicit FEA via `.k` keyword files and lsdyna batch execution — nonlinear dynamics, crash, forming, impact simulations. |
| `mapdl/` | `mapdl-sim` | Running Ansys MAPDL implicit FEA via PyMAPDL Python scripts — static/modal/thermal/harmonic analyses, `.rst` extraction, headless PyVista contour plots. |
| `icem/` | `icem-sim` | Running Ansys ICEM CFD meshing via Tcl batch scripts — tetra/hex mesh generation from `.tin` geometry, export to 143 solver formats (Fluent/CFX/MAPDL/Abaqus). |
| `calculix/` | `calculix-sim` | Running CalculiX (CCX) via Abaqus-dialect `.inp` input decks — open-source static/frequency/thermal FEA through sim one-shot execution on Linux. |
| `gmsh/` | `gmsh-sim` | Running Gmsh (finite-element mesh generator) via `.geo` DSL or Python API scripts — 2D/3D meshing, CAD import, export to CalculiX/OpenFOAM/FEniCS/SU2. |
| `su2/` | `su2-sim` | Running SU2 (open-source multi-physics CFD solver) via `.cfg` config files + `.su2` meshes — Euler/RANS/LES/adjoint design on Linux. |
| `lammps/` | `lammps-sim` | Running LAMMPS (classical molecular dynamics) via `.in` / `.lmp` scripts — LJ/EAM/Tersoff/ReaxFF potentials, NVE/NVT/NPT ensembles on Linux. |
| `scikit_fem/` | `scikit-fem-sim` | Running scikit-fem (pure-Python FEM library) via Python scripts — weak form assembly, function spaces, BCs, linear/nonlinear PDE solves. |
| `elmer/` | `elmer-sim` | Running Elmer FEM (open-source multi-physics FEM suite from CSC-IT) via `.sif` solver-input files + mesh directories — heat/elasticity/electromagnetics/fluid multiphysics on Linux. |
| `meshio/` | `meshio-sim` | Converting mesh formats between 20+ types (Gmsh/VTK/XDMF/CGNS/Abaqus/CalculiX/SU2/OpenFOAM) via pure-Python meshio library — the glue between sim's pre-processors and solvers. |
| `pyvista/` | `pyvista-sim` | Post-processing simulation results (.vtu/.vtk/.msh) via pyvista — Pythonic VTK for scalar stats, iso-surfaces, area/volume integration, headless PNG rendering. |
| `pymfem/` | `pymfem-sim` | Running PyMFEM (Python bindings for LLNL's MFEM C++ FEM library) via Python scripts — high-order H1/H(div)/H(curl) elements, UMFPack direct solve, PCG/GMRES iterative. |
| `openseespy/` | `openseespy-sim` | Running OpenSeesPy (PEER's structural earthquake-engineering FEM framework) via Python scripts — elastic/inelastic beams, fiber sections, pushover, time-history, modal/eigen. |
| `sfepy/` | `sfepy-sim` | Running SfePy (Simple Finite Elements in Python) via direct API — Mesh / Field / Term / Problem composition for Poisson, elasticity, NS, multi-physics weak forms. |
| `cantera/` | `cantera-sim` | Running Cantera (open-source thermodynamics / kinetics / transport from LBNL/Caltech) via Python scripts — equilibrium, reactor networks, premixed/diffusion flames, ignition delay. |
| `openmdao/` | `openmdao-sim` | Running OpenMDAO (NASA's open-source multidisciplinary design / analysis / optimization framework) via Python scripts — coupled MDA, gradient-based optimization, DOE, surrogates. |
| `fipy/` | `fipy-sim` | Running FiPy (NIST's pure-Python finite-volume PDE solver) via Python scripts — diffusion / convection / reaction PDEs on 1D/2D/3D structured or Gmsh meshes. |
| `pymoo/` | `pymoo-sim` | Running pymoo (Multi-Objective Optimization in Python) via Python scripts — NSGA-II/III, MOEA/D, GA, DE, PSO, CMAES — for benchmark and user-defined objective/constraint vectors. |
| `pyomo/` | `pyomo-sim` | Running Pyomo (Sandia's Python optimization modeling language) via Python scripts — LP/MIP/NLP/MINLP problems dispatched to HiGHS / GLPK / CBC / IPOPT / Gurobi / CPLEX. |
| `simpy/` | `simpy-sim` | Running SimPy (process-based discrete-event simulation in pure Python) via Python scripts — queueing systems, manufacturing lines, network protocols, hospital flow. |
| `trimesh/` | `trimesh-sim` | Running Trimesh (pure-Python triangular mesh processing) via Python scripts — STL/OBJ/PLY load, volume/area/inertia, watertight repair, boolean ops, ray casts, signed distance. |
| `devito/` | `devito-sim` | Running Devito (symbolic finite-difference DSL with JIT C codegen, Imperial College) via Python scripts — wave/heat/acoustic/elastic PDEs on regular grids, high-order stencils. |
| `coolprop/` | `coolprop-sim` | Running CoolProp (open-source REFPROP-equivalent thermophysical-property database) via Python scripts — Helmholtz-EoS for ~120 pure fluids + humid air, for HVAC / refrigeration / power-plant cycle analysis. |
| `scikit_rf/` | `scikit-rf-sim` | Running scikit-rf (Python RF/microwave network analysis) via Python scripts — Touchstone (.sNp) I/O, S-parameter math, transmission-line / CPW / waveguide media, SOLT/TRL calibration. |
| `pandapower/` | `pandapower-sim` | Running pandapower (Fraunhofer IEE Python power-system analysis with PYPOWER backend) via Python scripts — load flow, OPF, short-circuit, time-series on transmission/distribution networks. |
| `paraview/` | `paraview-sim` | Post-processing and visualizing large-scale CFD/FEA simulation results via ParaView's paraview.simple Python API — loading .vtu/.vtk/.case/.foam/.cgns data, applying filters (Clip/Slice/Contour/Threshold/StreamTracer), batch rendering PNG screenshots via pvpython/pvbatch, extracting quantitative metrics (IntegrateVariables, PlotOverLine, Calculator). |
| `hypermesh/` | `hypermesh-sim` | Pre-processing FE models via Altair HyperMesh -- CAD geometry import (STEP/IGES/CATIA/NX), surface and volume meshing (automesh/tetmesh/batchmesh), element quality checks (aspect/skew/jacobian), material/property/load assignment, and solver deck export (OptiStruct/Nastran/Abaqus/LS-DYNA/Radioss) through the hm Python API in batch mode. |

## Cross-skill conventions

The shared runtime contract — input classification (Category A/B/C),
acceptance semantics, Step-0 version probe, escalation triggers,
command surface, session lifecycle — lives in the **[`sim-cli/`](sim-cli/SKILL.md)** skill.

That skill is the source of truth for every rule that applies to more
than one driver. Load it alongside any driver skill. Per-driver
SKILL.mds own only the solver-specific layer.

Quick pointers into the shared skill:

- [`sim-cli/reference/input_classification.md`](sim-cli/reference/input_classification.md) — Category A / B / C
- [`sim-cli/reference/acceptance.md`](sim-cli/reference/acceptance.md) — `exit_code == 0` is not acceptance
- [`sim-cli/reference/version_awareness.md`](sim-cli/reference/version_awareness.md) — mandatory Step-0 `sim inspect session.versions` probe
- [`sim-cli/reference/lifecycle.md`](sim-cli/reference/lifecycle.md) — persistent and one-shot control patterns
- [`sim-cli/reference/command_surface.md`](sim-cli/reference/command_surface.md) — canonical `sim serve | run | connect | exec | inspect | disconnect`
- [`sim-cli/reference/escalation.md`](sim-cli/reference/escalation.md) — stop-and-report triggers

## Runtime dependency

These skills are useless without the [`sim`](../sim-cli/) runtime installed. See `../sim-cli/CLAUDE.md` for:
- The dual execution model (one-shot `sim run` vs persistent `sim serve` + `sim connect/exec/inspect`)
- Driver protocol (`DriverProtocol` in `sim.driver`)
- Driver registry (`sim.drivers.__init__`)
- HTTP server endpoints

For each solver, the matching driver lives at `sim-cli/src/sim/drivers/<solver>/`.

## When editing a skill

If you change a `SKILL.md`:

1. Keep the YAML frontmatter valid: `name` (letters / numbers / hyphens only) and `description` (starts with "Use when…", third person, focused on triggering conditions, NOT a workflow summary)
2. Don't move heavy reference content into SKILL.md — keep it in `reference/` and link
3. Update the `## File index` section if you add or rename files
4. The skill is the source of truth for the agent — drift between SKILL.md and the actual driver in `sim-cli/src/sim/drivers/<solver>/` is a bug; fix one or the other

## When adding a new solver skill

1. Create `sim-skills/<new-solver>/SKILL.md` with proper frontmatter
2. Mirror the section structure of the existing skills (Identity → Scope → Hard constraints → Required protocol → Input validation → File index)
3. Add the matching driver under `sim-cli/src/sim/drivers/<new-solver>/` and register it in `sim-cli/src/sim/drivers/__init__.py`
4. Add the new skill to the table in this CLAUDE.md and in `README.md`
