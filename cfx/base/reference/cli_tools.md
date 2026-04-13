# CFX Command-Line Tools Reference

## cfx5solve — Solver

**Purpose**: Run CFD simulations from definition files.

```bash
# Basic batch solve
cfx5solve -batch -def <file.def>

# With CCL overrides (modify BCs/settings without cfx5pre)
cfx5solve -batch -def <file.def> -ccl <overrides.ccl>

# Double precision
cfx5solve -batch -def <file.def> -double

# Restart from previous results
cfx5solve -batch -def <file.def> -ini <previous.res>

# Parallel (4 cores)
cfx5solve -batch -def <file.def> -par-dist "localhost*4"

# Change working directory
cfx5solve -batch -def <file.def> -chdir <directory>
```

**Key flags**:
| Flag | Description |
|------|-------------|
| `-batch` | No GUI, batch mode (required for automation) |
| `-def <file>` | Solver input definition file |
| `-ccl <file>` | CCL overrides to merge at solve time |
| `-double` | Double precision solver |
| `-ini <file>` | Initial values / restart from .res |
| `-par-dist <hosts>` | Parallel: `"host1*N,host2*M"` |
| `-chdir <dir>` | Set working directory |
| `-check-only` | Validate without solving |

**Output**: Produces `<name>_NNN.res` (results) and `<name>_NNN.out` (log).

## cfx5pre — Preprocessor

**Purpose**: Generate `.def` files from meshes + CCL.

```bash
# Batch mode with session file
cfx5pre -batch <session.pre>

# Load and modify a .cfx project
cfx5pre -cfx <project.cfx>

# Execute initial CCL commands
cfx5pre -initial-ccl "FLOW: Test\nEND"
```

## cfx5post — Post-Processor (CFD-Post)

**Purpose**: Visualize results, export data, generate images.

```bash
# Batch with session file
cfx5post -batch <session.cse> <results.res>

# Software rendering (no GPU needed)
cfx5post -batch <session.cse> -gr mesa

# GPU rendering (faster, better quality)
cfx5post -batch-gpu-rendering <session.cse>

# Interactive line mode
cfx5post -line <results.res>
```

## cfx5cmds — CCL Read/Write

**Purpose**: Extract CCL from `.def` files or inject modified CCL back.

```bash
# Extract CCL from .def to text file
cfx5cmds -read -def <file.def> -text <output.ccl>

# Write modified CCL back into .def
cfx5cmds -write -def <file.def> -text <modified.ccl>
```

**Limitation**: Cannot change mesh topology or geometry-related settings.

## cfx5mondata — Monitor Data Export

**Purpose**: Export convergence history to CSV.

```bash
# From results file
cfx5mondata -res <file.res> -out <output.csv>

# Show available variables
cfx5mondata -res <file.res> -showvars

# From run directory
cfx5mondata -dir <run_directory> -out <output.csv>
```

## cfx5perl — CFX Perl

**Purpose**: Run Perl scripts in CFX's Perl environment.

```bash
cfx5perl <script.pl>
```

Used internally by cfx5solve and for Power Syntax in CCL/CSE files.

## Typical automation workflow

```bash
# 1. Extract CCL from existing .def
cfx5cmds -read -def base.def -text base.ccl

# 2. Edit base.ccl (change BCs, solver settings)

# 3. Write changes back
cfx5cmds -write -def modified.def -text base.ccl

# 4. Solve
cfx5solve -batch -def modified.def -double

# 5. Post-process
cfx5post -batch post.cse modified_001.res

# 6. Export convergence data
cfx5mondata -res modified_001.res -out convergence.csv
```
