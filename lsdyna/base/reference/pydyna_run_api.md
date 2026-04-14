# PyDyna `run` API — launching LS-DYNA from Python

## Overview

`ansys.dyna.core.run.run_dyna()` is a thin Python wrapper around the LS-DYNA
executable. It does **not** require a gRPC server, Docker container, or any
client-server setup. Under the hood it just `subprocess.Popen`s the solver.

This is functionally equivalent to what the `sim` driver does — but called
from Python instead of from the CLI. Both paths converge on the same
`lsdyna_sp.exe i=<file.k>` command.

## Basic usage

```python
import os
from ansys.dyna.core.run import run_dyna

dynafile = "input.k"
dynadir = os.getcwd()
filepath = run_dyna(dynafile, working_directory=dynadir)
```

Key parameters:

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `input_file` | str | required | Path to the `.k` file |
| `working_directory` | str | `.` | Where d3plot / d3hsp / etc. are written |
| `ncpu` | int | 1 | Number of OpenMP threads |
| `memory` | str/int | "100m" | Memory allocation (e.g. `"500m"`, `"2000m"`) |
| `stream` | bool | True | If True, stream solver stdout to current stdout |
| `version` | str | None | Specific LS-DYNA version to use (overrides path discovery) |

## How LS-DYNA is located

`run_dyna` uses the `ansys-tools-path` package to discover LS-DYNA. Discovery order:

1. Path saved via `save-ansys-path --name dyna /path/to/lsdyna_sp.exe`
2. `AWP_ROOT<version>` environment variable → `ansys/bin/winx64/lsdyna_sp.exe`
3. PATH lookup
4. Default install paths under `Program Files/ANSYS Inc/v<version>/`

## Verifying success

`run_dyna` does **not** raise on solver failure (because LS-DYNA always
returns exit code 0). Always check post-conditions:

```python
import os

run_dyna("input.k", working_directory=wd)

# Output files exist
assert os.path.isfile(os.path.join(wd, "d3plot")), "No d3plot — solve failed"
assert os.path.isfile(os.path.join(wd, "lsrun.out.txt")), "No log file"

# Termination message in stdout (lsrun.out.txt captures it)
with open(os.path.join(wd, "lsrun.out.txt")) as f:
    log = f.read()
import re
assert re.search(r"N\s*o\s*r\s*m\s*a\s*l\s+t\s*e\s*r\s*m", log), "Error termination"
```

## Parametric sweeps

A common pattern from the Taylor bar example:

```python
import pathlib
from ansys.dyna.core.run import run_dyna

initial_velocities = [275e3, 300e3, 325e3, 350e3]
results = {}

for vel in initial_velocities:
    wd = pathlib.Path(f"./tb_vel_{vel:.0f}")
    wd.mkdir(exist_ok=True)
    write_input_deck(initial_velocity=vel, wd=str(wd))
    try:
        run_dyna("input.k", working_directory=str(wd), stream=False)
        results[vel] = post_process(wd)
    except Exception as e:
        print(f"Velocity {vel} failed: {e}")
```

`stream=False` suppresses per-cycle progress output in batch loops.

## Comparison with the `sim` driver

| | `run_dyna()` (PyDyna) | `sim run --solver ls_dyna` (this driver) |
|---|---|---|
| Caller environment | Python script | CLI / agent |
| Path discovery | `ansys-tools-path` | Manual scan of `Program Files/ANSYS Inc/v<ver>` |
| DLL handling | Implicit (assumes ANSYS bin on PATH) | Auto-augments PATH with Intel runtime |
| Run history | None — caller manages | `.sim/runs/NNN.json` |
| Return value | str (path) | `RunResult` dataclass |
| Best for | Inline use inside a parametric study | One-off agent invocations, run history needed |

The two paths are complementary, not competing. Use `run_dyna` inside a
PyDyna script you've already written; use `sim run` when the agent is just
executing one prepared `.k` file.

## Integration with the sim driver

You can write a Python script that uses `run_dyna` and then invoke that
script via `sim run` for unified history tracking:

```python
# my_parametric_study.py
from ansys.dyna.core.run import run_dyna
from ansys.dyna.core import Deck, keywords as kwd

# ... build deck, run_dyna, post-process ...

if __name__ == "__main__":
    main()
```

But for this to flow through the LS-DYNA driver detection (which expects
`.k` files), the script would need a custom solver tag — for now, just run
PyDyna scripts directly with `python my_script.py`.
