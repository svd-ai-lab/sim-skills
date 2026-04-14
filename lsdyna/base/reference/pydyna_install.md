# PyDyna Installation

## Package overview

PyDyna is the Python interface to LS-DYNA. It ships as a single PyPI package
`ansys-dyna-core` containing two functional modules:

| Module | Purpose | Requires |
|--------|---------|----------|
| `ansys.dyna.core.keywords` | Build/read/write `.k` keyword files programmatically | Pure Python — no LS-DYNA needed |
| `ansys.dyna.core.run` | Launch LS-DYNA solver as subprocess from Python | LS-DYNA installation + valid license |

**No gRPC, no Docker required** — both modules work locally with the system Python.

## Supported environments

- Python 3.9 - 3.12
- Windows, Linux, macOS

## Install (user mode)

```bash
python -m pip install -U pip
python -m pip install ansys-dyna-core
```

For DPF-based post-processing (recommended), also install:
```bash
python -m pip install ansys-dpf-core
```

For visualization in Jupyter:
```bash
python -m pip install pyvista
```

## Configure LS-DYNA path discovery

`run_dyna()` uses the `ansys-tools-path` package to find the LS-DYNA executable.
Register a path once with:

```bash
save-ansys-path --name dyna /path/to/lsdyna_sp.exe
```

After this, every `run_dyna(...)` call finds the solver automatically.

Alternatively, set environment variable `AWP_ROOT241` (or `AWP_ROOT<version>`)
pointing to the ANSYS root, and `ansys-tools-path` will discover LS-DYNA under
`ansys/bin/winx64/`.

## Install in developer mode

Clone and install editable:
```bash
git clone https://github.com/ansys/pydyna
cd pydyna
pip install -e .
```

## Install offline

For air-gapped machines, download the wheelhouse archive from the
[PyDyna releases page](https://github.com/ansys/pydyna/releases) for your
platform + Python version, then:

```bash
unzip ansys-dyna-core-<ver>-wheelhouse-Windows-3.12.zip -d wheelhouse
pip install ansys-dyna-core -f wheelhouse --no-index --upgrade --ignore-installed
```

## Verify installation

```python
import ansys.dyna.core
from ansys.dyna.core import Deck, keywords as kwd
from ansys.dyna.core.run import run_dyna

print(ansys.dyna.core.__version__)
print(ansys.dyna.core.AGENT_INSTRUCTIONS)  # path to bundled AI agent docs
```
