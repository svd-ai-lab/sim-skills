---
name: openfoam-sim
description: Use when running OpenFOAM v2206 cases through the sim runtime on a Linux box — meshing, decompose / mpirun / reconstruct, MPI parallel execution, classifying results PASS/SLOW_PASS/FAIL_*, and recovering from common failure modes via SSH-tunneled `sim connect`/`sim exec`.
---

# openfoam-sim

Control protocol for running OpenFOAM (v2206) through the `sim` runtime. The driver talks HTTP to a `sim serve` process on a Linux box where OpenFOAM is installed; agents on Windows/macOS connect over an SSH tunnel.

This is **NOT** a general OpenFOAM tutorial. It defines how an agent should drive `sim connect/exec/disconnect` to make OpenFOAM cases reproducible from a Windows/macOS host through HTTP, and how to recover from the most common failure modes — distilled from running **343 tutorials** (105 serial + 238 parallel) end-to-end.

## When to use

- Task involves OpenFOAM simulation orchestrated through sim CLI / sim-server
- Agent needs to mesh, decompose, run a solver, reconstruct, and extract results
- Need to choose between `Allrun` (preferred) and a manual `blockMesh + solver` pipeline
- Need to classify a case as PASS / SLOW_PASS / FAIL_* in a reproducible way
- Need to run cases in MPI parallel through `decomposePar / mpirun -np N / reconstructPar`

## Hard constraints

- **Always prefer `./Allrun` (with the dot) over manual pipelines.** `bash Allrun` breaks on tutorials whose first line is `cd "${0%/*}"`. >90% of "failures" we observed disappear once Allrun is respected.
- **Never modify `controlDict` with `sed`** to shrink endTime — it has corrupted multiple cases. If you need a faster run, use a smaller test case, not a butchered controlDict.
- **Never run cases inside `/tmp`.** `/tmp` is small, ephemeral, and gets cleaned. Use `/data/Chenyx/sim-openfoam-tests/` (or equivalent persistent disk path).
- **Never use `set -e` inside `#!openfoam` snippets.** Use `set +e` so the classifier can inspect non-zero exit codes.
- **Cap `numberOfSubdomains` to the server's core limit (100)** before running parallel cases. Check `system/decomposeParDict`.
- **Distinguish "solver advanced" from "solver hung."** A killed-by-timeout solver that reached `Time = 5.0` is `SLOW_PASS`, not a failure.
- **Read solver logs to judge progress, not shell exit code alone.** Bash's `timeout` may surface SIGFPE-looking messages that are not actual FPEs in the solver.

## Required protocol

### Step 0 — Parse task and identify physics
- **Category A (MUST ASK)**: solver family (incompressible / compressible / multiphase / …), Re or Mach number range, geometry source (built-in tutorial vs STL), boundary conditions, end time / steady-state, acceptance criteria
- **Category B (MAY DEFAULT)**: turbulence model (default: kOmegaSST for RANS, Smagorinsky for LES), discretisation order (default: 2nd), parallel cores (default: 4)
- **Category C (INFER)**: closest matching tutorial — search `$FOAM_TUTORIALS` by solver family + geometry type

### Step 1 — Connect
```bash
# From client through SSH tunnel: ssh -p 2333 -L 7600:localhost:8080 user@linux-host
sim --host localhost --port 7600 connect --solver openfoam
sim --host localhost --port 7600 inspect session.summary
# → expect connected:true, openfoam.version:v2206
```

### Step 2 — Find / copy a starting tutorial
OpenFOAM ships **462 tutorial cases** that are the single best source of truth for "how to set up X". When you need new physics, find the closest tutorial and copy its structure — don't write `0/`, `constant/`, `system/` files from scratch.

```bash
sim exec -c '#!openfoam
ls $FOAM_TUTORIALS/incompressible/simpleFoam/'

sim exec -c '#!openfoam
mkdir -p /data/Chenyx/sim-openfoam-tests/runs
rm -rf /data/Chenyx/sim-openfoam-tests/runs/my_case
cp -r $FOAM_TUTORIALS/incompressible/simpleFoam/motorBike \
      /data/Chenyx/sim-openfoam-tests/runs/my_case'
```

### Step 3 — Customise the case (only what you need)
**Allowed:** edit `0/U`, `0/p`, `0/T` for new BC values; `constant/transportProperties`, `constant/turbulenceProperties`; replace `constant/triSurface/*.stl`; change `system/blockMeshDict`. **Not allowed:** edit `controlDict` with `sed` to shrink endTime — see hard constraints.

### Step 4 — Run via Allrun (preferred path)
```bash
sim exec -c '#!openfoam
set +e
cd /data/Chenyx/sim-openfoam-tests/runs/my_case
chmod +x Allrun
timeout 600 ./Allrun > out.log 2>&1
echo exit=$?'
```

### Step 5 — Classify and extract
Use the classifier from [`reference/success_patterns.md`](reference/success_patterns.md):

1. `exit 0` + `End` in log → **PASS**
2. `exit 124/137` + `Time = X > 0` in solver log → **SLOW_PASS** (success)
3. `FOAM FATAL` + "cannot find file" → **FAIL_PRECHECK** (run pre-step)
4. `FOAM FATAL` + FPE/NaN → **FAIL_RUNTIME** (numerical bug)
5. Otherwise → **FAIL_WORKFLOW**

Extract:
```bash
sim exec -c '#!openfoam
cd /data/Chenyx/sim-openfoam-tests/runs/my_case
ls -d [0-9]* | tail -3
postProcess -func "patchAverage(name=outlet, U)" -latestTime
postProcess -func "forceCoeffs"'
```

### Step 6 — Disconnect
```bash
sim disconnect
```

## Failure recovery quick reference

| Symptom | Most likely cause | Fix |
|---|---|---|
| `cannot find file "0/p"` | Skipped `cp -r 0.orig 0` (or `restore0Dir`) | Use `./Allrun` |
| `cannot find file "constant/reactions"` | Skipped `chemkinToFoam` | Use `./Allrun` |
| `Cannot read file ".../geometry/X.vtk"` | Skipped geometry copy from `$FOAM_TUTORIALS/resources/` | Use `./Allrun` |
| Solver started, no `Time =` ever appears | snappyHexMesh consumed entire timeout | Increase timeout, or split into Allrun.pre + Allrun |
| `Floating point exception` from bash, but solver log shows progress | Bash's misleading SIGFPE message; solver actually advancing | Read solver log; classify as SLOW_PASS |
| `numberOfSubdomains 128` | Server has fewer cores | Edit decomposeParDict to ≤100 |
| `bash: Allrun: Not a directory` | Used `bash Allrun` instead of `./Allrun` | Use `./Allrun` |
| `exit 1` very fast, no logs | Allrun's `set -e` aborted on first error | Read out.log to find the failed command |

For deeper triage, see [`reference/failure_patterns.md`](reference/failure_patterns.md) (full triage tree).

## Tutorial categories

| Looking for ... | Browse this category |
|---|---|
| Incompressible flow | `$FOAM_TUTORIALS/incompressible/{icoFoam,simpleFoam,pimpleFoam,pisoFoam}/` |
| Compressible / shock / supersonic | `$FOAM_TUTORIALS/compressible/{rhoCentralFoam,rhoPimpleFoam,sonicFoam}/` |
| Combustion | `$FOAM_TUTORIALS/combustion/{reactingFoam,XiFoam,fireFoam}/` |
| Heat transfer (CHT, buoyancy) | `$FOAM_TUTORIALS/heatTransfer/{buoyantSimpleFoam,chtMultiRegionFoam}/` |
| Multiphase VOF | `$FOAM_TUTORIALS/multiphase/{interFoam,interIsoFoam,compressibleInterFoam}/` |
| Multiphase Eulerian | `$FOAM_TUTORIALS/multiphase/{twoPhaseEulerFoam,multiphaseEulerFoam}/` |
| Lagrangian particles / sprays | `$FOAM_TUTORIALS/lagrangian/{sprayFoam,reactingParcelFoam,MPPICFoam}/` |
| DNS / forced isotropic turbulence | `$FOAM_TUTORIALS/DNS/dnsFoam/` |
| Stress / FEA | `$FOAM_TUTORIALS/stressAnalysis/` |
| Mesh generation | `$FOAM_TUTORIALS/mesh/{blockMesh,snappyHexMesh,foamyHexMesh}/` |
| Adjoint / shape opt | `$FOAM_TUTORIALS/incompressible/adjointOptimisationFoam/` |

### Known-good tutorials (verified PASS via sim)

| Use case | Tutorial path |
|---|---|
| Simplest incompressible | `incompressible/icoFoam/cavity/cavity` |
| RANS external aero | `incompressible/simpleFoam/motorBike` |
| Multiphase free surface | `multiphase/interFoam/laminar/damBreak/damBreak` |
| Multi-region CHT | `heatTransfer/chtMultiRegionSimpleFoam/multiRegionHeaterRadiation` |
| DNS turbulence | `DNS/dnsFoam/boxTurb16` |
| Combustion | `combustion/reactingFoam/laminar/counterFlowFlame2D` |
| Compressible airfoil | `compressible/rhoSimpleFoam/aerofoilNACA0012` |
| FEA stress | `stressAnalysis/solidDisplacementFoam/plateHole` |

For the full list (PASS / SLOW_PASS / FAIL with status), see `docs/parallel_test_results.md` and `docs/tutorial_test_results.md`.

## Snippet conventions

Every OpenFOAM snippet sent through `sim exec` should:

1. Start with `#!openfoam` shebang
2. Use `set +e` (NOT `set -e`) so the classifier can inspect non-zero exits
3. Run from absolute paths under `/data/Chenyx/sim-openfoam-tests/` — never `/tmp`
4. Print a final JSON object on the last stdout line for `parse_output()`:
   ```bash
   echo '{"ok": true, "case": "my_case", "final_time": "500"}'
   ```
5. Pipe heavy solver output through `tail -n 20`

## Storage convention

```
/data/Chenyx/sim-openfoam-tests/      persistent root, NOT /tmp
├── runs/        active workspace for one-off cases
├── serial/      batch tests, serial cases
├── parallel/    batch tests, MPI cases
├── diag/        deep-diagnosis runs
├── runner/      run_case.sh + helpers
└── results/     *.txt result tables
```

`/tmp` is small (often <30 GB) and gets cleaned by tmpfs at boot. Multi-region and snappyHexMesh cases routinely produce 100s of MB each.

## File index

### Top-level
- `SKILL.md` — this file

### `reference/` — distilled patterns
- `reference/success_patterns.md` — the seven patterns that consistently work; read before writing a runner / snippet / batch job
- `reference/failure_patterns.md` — triage tree and minimal fixes for FAIL_PRECHECK / FAIL_RUNTIME / FAIL_WORKFLOW / FAIL_WORKFLOW_NOPROGRESS / NO_ALLRUN / SKIP_NP

### `docs/` — runner script + test results
- `docs/tutorial_runner_v2.md` — the canonical runner script and PASS / SLOW_PASS / FAIL classifier function
- `docs/tutorial_test_plan.md` — the plan that produced the 343-tutorial run
- `docs/tutorial_test_results.md` — per-tutorial results table for **serial** runs
- `docs/parallel_test_results.md` — per-tutorial results table for **MPI parallel** runs
- `docs/prompt_for_linux_claude.md` — prompt template for delegating Linux-side OpenFOAM work to a Claude session

### `tests/` — pytest unit + integration
- `tests/test_driver.py` — driver unit + integration tests; integration tests need a running `sim serve` at `SIM_SERVER_HOST:7600`
- `tests/fixtures/cavity_setup.sh` — bash fixture for the lid-driven cavity
- `tests/fixtures/hello_foam.py` — minimal Python fixture for driver smoke test

## Requirements

- A Linux host with OpenFOAM v2206 sourced (`source $WM_PROJECT_DIR/etc/bashrc`)
- `sim-cli` installed on that host, `sim serve` running
- SSH tunnel from the agent's host: `ssh -p <port> -L 7600:localhost:8080 user@linux-host`
- Persistent disk for cases (do NOT use `/tmp`)
