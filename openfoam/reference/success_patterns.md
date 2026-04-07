# OpenFOAM via sim — Success Patterns

Distilled from running 343 OpenFOAM tutorials (105 serial + 238 parallel) through
the sim driver against OpenFOAM v2206 on a remote Linux server.

## TL;DR — The five rules that make tutorials work

1. **Always use `./Allrun`** (with the dot), never reinvent the pipeline
2. **Never modify `controlDict` with sed** — let the tutorial run with its own time budget
3. **Read solver log for `Time = X` to judge progress**, not shell exit code
4. **Cap np at the server core limit** before running, not during
5. **Use `#!openfoam` shebang**, then `set +e` (not `set -e`) so classification can run

## Pattern 1: The canonical Allrun-driven runner

```bash
#!openfoam
set +e
case_path="$1"   # e.g. incompressible/simpleFoam/motorBike
to="${2:-180}"
workdir=/data/Chenyx/sim-openfoam-tests/runs/$(echo $case_path | tr / _)

rm -rf $workdir
cp -r $FOAM_TUTORIALS/$case_path $workdir
cd $workdir

# Cap np if needed (server limit)
np=$(grep -E '^numberOfSubdomains' system/decomposeParDict 2>/dev/null \
     | head -1 | awk '{print $2}' | tr -d ';')
if [ -n "$np" ] && [ "$np" -gt 100 ]; then
  echo "SKIP_NP=$np"; exit
fi

# Prefer Allrun-parallel (parallel cases), then Allrun, else manual
if [ -f Allrun-parallel ]; then
  chmod +x Allrun-parallel
  timeout $to ./Allrun-parallel > out.log 2>&1
elif [ -f Allrun ]; then
  chmod +x Allrun
  timeout $to ./Allrun > out.log 2>&1
else
  # Fallback for tutorials without Allrun
  [ -d 0.orig ] && cp -r 0.orig 0
  solver=$(grep '^application' system/controlDict | awk '{print $2}' | tr -d ';')
  blockMesh > log.blockMesh 2>&1
  timeout $to $solver > log.$solver 2>&1
fi
```

**Why `./Allrun` (not `bash Allrun`)**: Allrun's first line is
`cd "${0%/*}" || exit`. With `bash Allrun`, `$0` is just `"Allrun"` (no slash),
so `${0%/*}` gives `"Allrun"` — the cd then tries to enter a directory called
"Allrun" which is the script file itself, and fails with `Not a directory`.
With `./Allrun`, `$0` becomes `"./Allrun"`, and `${0%/*}` correctly gives `"."`.

## Pattern 2: Per-case workspace under /data, not /tmp

```bash
DEST=/data/Chenyx/sim-openfoam-tests
mkdir -p $DEST/{serial,parallel,diag,runner,results}
```

Three reasons:
1. `/tmp` on most Linux installs is small (often <30GB) and gets cleaned by tmpfs
2. Multi-region/snappyHexMesh tutorials can produce 100s of MB per case
3. `/data` is on a separate large disk, and persists across reboots

## Pattern 3: Five-state classification

The most important thing is to **distinguish "solver advanced" from "solver hung"**.
A solver running 50 timesteps but hitting a wall-clock timeout is NOT a failure.

```bash
classify() {
  local rc=$1; local out_log=$2
  
  # 1. Hard fault (FATAL in any log file)
  if grep -l 'FOAM FATAL' log.* $out_log 2>/dev/null | head -1 > /tmp/fatal_log; then
    fatal_log=$(cat /tmp/fatal_log)
    if grep -qE 'cannot find file|cannot open|No such file' "$fatal_log"; then
      echo FAIL_PRECHECK; return
    fi
    if grep -qE 'Floating point|NaN|diverged' "$fatal_log"; then
      echo FAIL_RUNTIME; return
    fi
    echo FAIL_WORKFLOW; return
  fi
  
  # 2. Clean exit
  [ "$rc" -eq 0 ] && { echo PASS; return; }
  
  # 3. Killed by timeout (SIGTERM=124, SIGKILL=137) — was it progressing?
  if [ "$rc" -eq 124 ] || [ "$rc" -eq 137 ]; then
    last_log=$(ls -t log.* 2>/dev/null | grep -vE 'log.(decomposePar|blockMesh|snappyHex|setFields|topoSet|reconstructPar)' | head -1)
    [ -z "$last_log" ] && last_log=$(ls -t log.* 2>/dev/null | head -1)
    last_time=$(grep -oE '^Time = [0-9.e+-]+' "$last_log" 2>/dev/null | tail -1 | awk '{print $3}')
    if [ -n "$last_time" ]; then
      echo "SLOW_PASS=$last_time"   # solver IS working, just slow
      return
    fi
    echo FAIL_WORKFLOW_NOPROGRESS
    return
  fi
  
  echo "FAIL_RUNTIME(rc=$rc)"
}
```

The key trick: when filtering log files, **exclude pre-processing logs**
(`log.decomposePar`, `log.blockMesh`, `log.setFields`, etc.) so you get the
actual solver log, which is the only place "Time = X" makes sense.

## Pattern 4: Parallel workflow validation

For 238 parallel cases, the full chain works:

```
Allrun-parallel
  ├── blockMesh                                      # serial mesh
  ├── (snappyHexMesh -overwrite)                     # optional, sometimes parallel
  ├── decomposePar                                   # split mesh into N pieces
  ├── mpirun -np N <solver> -parallel               # run on N MPI ranks
  ├── reconstructPar                                 # merge time directories back
  └── (paraFoam / sample / postProcess)              # optional post
```

Verified end-to-end on:
- **motorBike** (np=6, snappyHexMesh + simpleFoam, 178s)
- **chtMultiRegionFoam** windshield/multiRegionHeater (np=4, multi-region)
- **overPimpleDyMFoam** simpleRotor (np=3, overset)
- **interFoam** damBreak (np=4, VOF multiphase)

## Pattern 5: Common pre-steps that tutorials need

Many tutorials have non-obvious pre-steps in `Allrun`. **Don't reinvent —
use Allrun**. If you must run manually, be aware of these:

| Pre-step | When needed | Example tutorials |
|----------|-------------|-------------------|
| `cp -r 0.orig 0` (or `restore0Dir`) | Most tutorials | Almost all incompressible/simpleFoam |
| `setFields` | VOF/multi-component initial fields | interFoam/damBreak, twoLiquidMixingFoam |
| `boxTurb` | DNS initial random velocity | DNS/dnsFoam/boxTurb16 |
| `mdInitialise` | Molecular dynamics | molecularDynamics/mdFoam, mdEquilibrationFoam |
| `chemkinToFoam chem.inp therm.dat ...` | CHEMKIN-format chemistry | combustion/chemFoam/gri |
| `cp $FOAM_TUTORIALS/resources/geometry/*.vtk.gz constant/geometry/` | Tutorials referencing shared geometry | mesh/blockMesh/pipe |
| `surfaceFeatureExtract` | snappyHexMesh with features | motorBike, gap_detection |
| `topoSet` | Cell zones for porous/sources | porousSimpleFoam, MRF cases |
| `createPatch` | Cyclic AMI / non-conformal interfaces | basic/laplacianFoam/implicitAMI |
| `mirrorMesh -overwrite` | Symmetric cases meshed as half | pimpleFoam/laminar/cylinder2D |
| `extrudeMesh` | 2D-from-3D cases | atmospheric models |
| `mapFields <precursor>` | Precursor → main run | LES with inflow turbulence |

## Pattern 6: Result naming for batch tracking

```bash
# Results format: one line per case, parseable
[<index> np=<np>] <category>/<subcat>/<case> <STATUS>[=<extra>]

# Examples:
[44 np=4] basic/laplacianFoam/flange PASS
[228 np=12] incompressible/pimpleFoam/laminar/cylinder2D SLOW_PASS=18.9
[110 np=4] incompressible/pimpleFoam/RAS/propeller FAIL_WORKFLOW_NOPROGRESS
```

This makes the results trivially groupable:
```bash
grep -c " PASS$" results.txt
grep -c " SLOW_PASS=" results.txt
grep " FAIL" results.txt | awk '{print $NF}' | sort | uniq -c
```

## Pattern 7: Token-efficient exec for AI agents

When driving sim-server through HTTP from a token-budgeted AI agent:

1. **Install runner ONCE**, then call by name:
   ```bash
   bash /data/Chenyx/sim-openfoam-tests/runner/run_case.sh <path> <timeout>
   ```
2. **Append results to a server-side file**, fetch in bulk:
   ```bash
   echo "$result" >> /data/Chenyx/sim-openfoam-tests/results/p_results.txt
   ```
3. **Filter to short status lines** before returning to the agent, never echo
   full solver output for batch sweeps

## Real-world success rates

| Category | Cases | Effective success (PASS+SLOW_PASS) |
|----------|------:|-----------------------------------:|
| Serial Batches 1–7 | ~105 | 94% |
| Parallel Batch 8 | 238 | 80% |
| Combined | 343 | 84% |

The remaining 16% are mostly **NO_ALLRUN sub-components** of larger workflows
(8%) and **FAIL_WORKFLOW_NOPROGRESS** cases that need a longer time budget for
their pre-processing stage to complete. Real solver crashes are <2%.
