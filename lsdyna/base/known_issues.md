# LS-DYNA Known Issues

## KI-001: Exit code 0 on error termination
**Severity**: Critical
**Symptom**: LS-DYNA returns exit code 0 even when the solve fails with `E r r o r    t e r m i n a t i o n`.
**Workaround**: Always check stdout for the spaced-character termination message. The driver's `parse_output()` detects this pattern automatically.

## KI-002: DLL dependency on Windows (libiomp5md.dll)
**Severity**: High
**Symptom**: `lsdyna_sp.exe` fails with "cannot open shared object file: libiomp5md.dll" when run from non-ANSYS shells.
**Root cause**: Intel OpenMP runtime DLL is in `<AWP_ROOT>/tp/IntelCompiler/<ver>/winx64/`, not on the default PATH.
**Workaround**: The driver's `_runtime_env()` method automatically augments PATH with the Intel compiler directory. For manual runs, set `AWP_ROOT241` and source the `lsdynaintelvar.bat` script.

## KI-003: LSDYNA.exe is a launcher, not the solver
**Severity**: Low
**Symptom**: `LSDYNA.exe` (1.3 MB) appears to be the solver but is actually a launcher/wrapper.
**Fix**: The driver searches for `lsdyna_sp.exe` (253 MB) first, which is the actual single-precision solver.

## KI-004: Fixed-width card misalignment
**Severity**: High
**Symptom**: `*** Error 10121 (KEY+121) *COMMAND found out of place` — data cards misread as keywords.
**Root cause**: Data values not properly aligned to 8-character field boundaries. For example, `*PART` requires exactly 2 data lines; missing lines cause the next keyword to be read as data.
**Workaround**: Use the LS-DYNA keyword reference for exact card formats. Always provide all required data cards, even if values are default (0).

## KI-005: LS-PrePost batch mode unreliable
**Severity**: Medium
**Symptom**: `lsprepost4.10_x64.exe c=<cfile>` segfaults or ignores the command file when run from bash/MSYS2 shells.
**Root cause**: LS-PrePost has Windows GUI dependencies that conflict with MSYS2/Cygwin environment.
**Workaround**: Launch LS-PrePost through PowerShell (`Start-Process`) or `cmd.exe`. For automated rendering, consider using ParaView with the LS-DYNA reader plugin.

## KI-006: d3hsp contains primary solver diagnostics
**Severity**: Info
**Symptom**: stdout contains only progress messages; detailed error messages, warnings, and convergence info are in the `d3hsp` file.
**Note**: The driver reads `d3hsp` after solve completion to capture termination status if not present in stdout.

## KI-007: Implicit solver requires additional control cards
**Severity**: Medium
**Symptom**: Implicit analysis fails or doesn't converge without proper control cards.
**Fix**: Implicit requires at minimum: `*CONTROL_IMPLICIT_GENERAL` (IMFLAG=1), `*CONTROL_IMPLICIT_SOLUTION`, and `*CONTROL_IMPLICIT_AUTO`. See `base/reference/control_cards.md`.
