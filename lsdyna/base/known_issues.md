# LS-DYNA Known Issues

## KI-001: Exit code 0 on error termination
**Severity**: Critical
**Symptom**: LS-DYNA returns exit code 0 even when the solve fails with `E r r o r    t e r m i n a t i o n`.
**Workaround**: Always check stdout (or `lsrun.out.txt` when running via PyDyna's `run_dyna`) for the spaced-character termination message. The driver's `parse_output()` detects this pattern automatically.

## KI-002: DLL dependency on Windows (libiomp5md.dll)
**Severity**: High
**Symptom**: `lsdyna_sp.exe` fails with "cannot open shared object file: libiomp5md.dll" when run from non-ANSYS shells.
**Root cause**: Intel OpenMP runtime DLL is in `<AWP_ROOT>/tp/IntelCompiler/<ver>/winx64/`, not on the default PATH.
**Workaround**:
- The `sim` driver's `_runtime_env()` automatically augments PATH with the Intel compiler directory.
- For PyDyna's `run_dyna()`: run from a shell that has sourced `lsdynaintelvar.bat`, or pre-set `AWP_ROOT241` so `ansys-tools-path` discovers the bin directory and PATH order is correct.
- For manual runs: source `<AWP_ROOT>/ansys/bin/winx64/lsprepost410/LS-Run/lsdynaintelvar.bat`.

## KI-003: LSDYNA.exe is a launcher, not the solver
**Severity**: Low
**Symptom**: `LSDYNA.exe` (1.3 MB) appears to be the solver but is actually a launcher/wrapper.
**Fix**: The driver searches for `lsdyna_sp.exe` (253 MB) first, which is the actual single-precision solver.

## KI-004: Fixed-width card misalignment
**Severity**: High
**Symptom**: `*** Error 10121 (KEY+121) *COMMAND found out of place` — data cards misread as keywords.
**Root cause**: Data values not properly aligned to 8-character field boundaries. For example, `*PART` requires exactly 2 data lines; missing lines cause the next keyword to be read as data.
**Workaround**:
- **Best**: Use the PyDyna `keywords` API (`base/reference/pydyna_keywords_api.md`) — it formats fields automatically and can never produce misaligned cards.
- For hand-written `.k` files: use the LS-DYNA keyword reference for exact card formats. Always provide all required data cards, even if values are default (0).

## KI-005: LS-PrePost batch mode unreliable
**Severity**: Medium
**Symptom**: `lsprepost4.10_x64.exe c=<cfile>` segfaults or ignores the command file when run from bash/MSYS2 shells.
**Root cause**: LS-PrePost has Windows GUI dependencies that conflict with MSYS2/Cygwin environment.
**Workaround**: **Use `ansys-dpf-core` for headless post-processing instead** — it reads d3plot directly in Python and works reliably across all environments. See `base/workflows/pydyna_taylor_bar/README.md` for the DPF pattern. Reserve LS-PrePost for interactive human review.

## KI-006: d3hsp contains primary solver diagnostics
**Severity**: Info
**Symptom**: stdout contains only progress messages; detailed error messages, warnings, and convergence info are in the `d3hsp` file.
**Note**: The driver reads `d3hsp` after solve completion to capture termination status if not present in stdout.

## KI-007: Implicit solver requires additional control cards
**Severity**: Medium
**Symptom**: Implicit analysis fails or doesn't converge without proper control cards.
**Fix**: Implicit requires at minimum: `*CONTROL_IMPLICIT_GENERAL` (IMFLAG=1), `*CONTROL_IMPLICIT_SOLUTION`, and `*CONTROL_IMPLICIT_AUTO`. See `base/reference/control_cards.md`.

## KI-008: PyDyna keyword class names follow MAT_xxx numbering, not free-text aliases
**Severity**: Low
**Symptom**: `from ansys.dyna.core import keywords as kwd; mat = kwd.MatPlasticKinematic(...)` may not exist; class is `kwd.Mat003`.
**Workaround**: PyDyna auto-generates classes from LS-DYNA's `MAT_NNN` numbering. `*MAT_PLASTIC_KINEMATIC` is `MAT_003` → `kwd.Mat003`. Many materials also have name aliases (`kwd.MatElastic` for `Mat001`), but for non-trivial materials use the numeric form. Check available classes with `dir(kwd)`.

## KI-009: PyDyna `run_dyna()` doesn't raise on solve failure
**Severity**: Medium
**Symptom**: `run_dyna("input.k")` returns successfully even when LS-DYNA error-terminates (because LS-DYNA exit code is 0).
**Workaround**: Always assert post-conditions:
```python
run_dyna("input.k", working_directory=wd)
assert os.path.isfile(os.path.join(wd, "d3plot")), "No d3plot — check d3hsp for errors"

with open(os.path.join(wd, "lsrun.out.txt")) as f:
    log = f.read()
import re
assert re.search(r"N\s*o\s*r\s*m\s*a\s*l\s+t\s*e\s*r\s*m", log), "Error termination"
```

## KI-010: ansys-tools-path discovery may pick wrong LS-DYNA version
**Severity**: Low
**Symptom**: When multiple ANSYS versions are installed, `run_dyna()` may pick a version different from the one expected.
**Workaround**: Pin explicitly with `save-ansys-path --name dyna /path/to/specific/lsdyna_sp.exe` or set `AWP_ROOT<version>` to the desired version's root. The `sim` driver, by contrast, returns all detected installs sorted by version (newest first) — explicit path control via `extra["exe"]` in `SolverInstall`.

## KI-011: DPF requires a separate ANSYS DPF server installation
**Severity**: Medium
**Symptom**: `import ansys.dpf.core` works but `dpf.Model(ds)` fails with "Unable to locate any Ansys installation".
**Root cause**: `ansys-dpf-core` is the Python client; it needs a DPF server (bundled with ANSYS install) to actually process results.
**Workaround**: Set `AWP_ROOT241` env var pointing to ANSYS install, or pass `ansys_path=` to `dpf.start_local_server()`. DPF picks the server from `<AWP_ROOT>/aisol/bin/winx64/Ans.Dpf.Grpc.exe`.
