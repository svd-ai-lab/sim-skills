# LS-DYNA Output Files

## Primary output files

| File | Format | Contents | When to check |
|------|--------|----------|---------------|
| `d3plot` | Binary | Full-field results (displacements, stresses, strains) | Post-processing visualization |
| `d3hsp` | Text | Detailed solver log, input echo, diagnostics | Debugging, convergence check |
| `d3dump01` | Binary | Restart file | Continuing interrupted runs |
| `glstat` | Text | Global statistics (energies, timestep, velocities) | Energy balance verification |
| `matsum` | Text | Per-material summaries (KE, IE, forces) | Material-level verification |
| `messag` | Text | Solver messages, warnings, timing | Quick status check |
| `status.out` | Text | Short status summary | Quick pass/fail check |

## How to verify success

### 1. Check termination type (stdout or d3hsp)
```
N o r m a l    t e r m i n a t i o n     ← SUCCESS
E r r o r    t e r m i n a t i o n       ← FAILURE
```
**Warning**: Exit code is 0 even for error termination!

### 2. Check cycle count and time
```
Problem time       =    1.0000E+00     ← Should match ENDTIM
Problem cycle      =      7129         ← Should be reasonable for the model
```

### 3. Check energy balance (glstat)
Format of glstat:
```
 time    kinetic energy  internal energy  ...  total energy  ...
 0.000E+00  0.000E+00      0.000E+00     ...  0.000E+00   ...
 1.000E-02  1.234E-05      5.678E-04     ...  5.802E-04   ...
```
Total energy should be approximately conserved (within a few percent).

### 4. Check for warnings in d3hsp
Search for `*** Warning` — common issues:
- Negative volume elements (severe mesh distortion)
- Contact penetration
- Small timestep due to element quality

## d3plot visualization

The `d3plot` file (and continuation files `d3plot01`, `d3plot02`, ...) contains
binary results for visualization in LS-PrePost or third-party post-processors.

**LS-PrePost** is the standard post-processor:
- GUI application: `lsprepost4.10_x64.exe`
- Open: File → Open → select `d3plot`
- Fringe plot: Post → FringeComponent → select result type
- Animation: Use timestep slider

**Alternative post-processors:**
- ParaView (with LS-DYNA reader plugin)
- EnSight
- Ansys Mechanical APDL (via d3plot import)

## Parsing solver output programmatically

### From stdout
```python
# Normal termination check (spaced characters)
import re
normal = re.search(r"N\s*o\s*r\s*m\s*a\s*l\s+t\s*e\s*r\s*m", stdout)

# Cycle count
cycles = re.search(r"Problem cycle\s*=\s*(\d+)", stdout)

# Elapsed time
elapsed = re.search(r"Elapsed time\s+([\d.]+)\s+seconds", stdout)
```

### From glstat
```python
# glstat is space-delimited columnar data
# Columns: time, KE, IE, TE, ratio, ...
with open("glstat") as f:
    for line in f:
        if line.strip() and not line.startswith(" t"):
            fields = line.split()
            time, ke, ie = float(fields[0]), float(fields[1]), float(fields[2])
```
