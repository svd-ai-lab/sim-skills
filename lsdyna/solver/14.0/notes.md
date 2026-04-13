# LS-DYNA R14.0 (Ansys 2024 R1) Notes

## Version info

| Field | Value |
|-------|-------|
| Version | smp s R14 |
| Revision | R14.1-205-geb5348f751 |
| License | AnLicVer: 2024 R1 (20231025+39429f6) |
| Platform | WINDOWS X64 SSE2 |
| Compiler | Intel Fortran XE 2019 MSVC++ 2019 |
| Precision | Single precision (I4R4) for `lsdyna_sp.exe` |

## Executables

Located at `<AWP_ROOT241>/ansys/bin/winx64/`:

| Executable | Size | Purpose |
|-----------|------|---------|
| `LSDYNA.exe` | 1.3 MB | Launcher (not the solver) |
| `lsdyna_sp.exe` | 253 MB | Single precision SMP solver |
| `lsdyna_dp.exe` | 299 MB | Double precision SMP solver |
| `lsdyna_mpp_sp_impi.exe` | 238 MB | SP + Intel MPI |
| `lsdyna_mpp_dp_impi.exe` | 263 MB | DP + Intel MPI |
| `lsdyna_mpp_sp_msmpi.exe` | 238 MB | SP + Microsoft MPI |
| `lsdyna_mpp_dp_msmpi.exe` | 262 MB | DP + Microsoft MPI |

## Runtime dependencies

### Intel runtime DLLs
Required DLL: `libiomp5md.dll` from `<AWP_ROOT241>/tp/IntelCompiler/2023.1.0/winx64/`

The driver automatically adds this to PATH. For manual execution:
```batch
call "%AWP_ROOT241%\ansys\bin\winx64\lsprepost410\LS-Run\lsdynaintelvar.bat"
lsdyna_sp.exe i=input.k
```

### Environment variables
- `AWP_ROOT241`: Points to ANSYS v241 installation root (auto-detected by the driver)
- `LSTC_LICENSE`: License type — the ANSYS license server handles this automatically

## Known quirks

1. **License warning**: `*** WARNING LSTC_LICENSE set to unknown type "Ansys"` appears on every run — this is harmless and expected when using ANSYS licensing.

2. **Exit code always 0**: Even on error termination, the solver returns exit code 0. The driver checks stdout for the termination message pattern.

3. **Memory from default**: If no `memory=` argument, defaults to 100,000,000 words (~400 MB for SP). Sufficient for small models.

## LS-PrePost

Version 4.10 is included at `<AWP_ROOT241>/ansys/bin/winx64/lsprepost410/`.
- GUI-only post-processor
- Command file batch mode (`c=`) has reliability issues in MSYS2/Cygwin shells
- Use PowerShell or cmd.exe for command file execution
