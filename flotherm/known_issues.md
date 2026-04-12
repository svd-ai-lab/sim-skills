# Known Issues — flotherm-sim

## ISSUE-001: Batch mode (`flotherm.bat -b`) non-functional in Flotherm 2504

**Date discovered**: 2026-04-01  
**Severity**: Critical — blocks headless solve via `flotherm.bat -b`  
**Status**: **WORKAROUND FOUND** (2026-04-12) — direct `translator.exe` + `solexe.exe` bypasses floserv entirely  

### Symptom

`flotherm.bat -b <project>` (which calls `floserv.exe 16 -b <project>`) always produces:

```
stderr:   registerStart runTable exception: invalid map<K, T> key
          unregisterStart exception: invalid map<K, T> key

floerror.log:
  ERROR   E/11029 - Failed unknown file type No reader for this file type - <project_dir>
  ERROR   E/9012 - Too few grid-cells to be solved NX = 1 and NY = 1
  INFO    I/9033 - Total number of Grid Cells are: 1
  INFO    I/9032 - Translator completed Errors: 1 Warnings: 0 Informationals: 1
```

The solve **never runs**. Zero field files are modified. Exit code is misleadingly `0`.

### Root cause analysis

1. `floserv.exe 16 -b <project>` attempts to initialize the RunTable (a C++ `std::map` that tracks batch job entries defined in `config/server.cfg`).
2. The RunTable initialization throws `invalid map<K, T> key` — the key lookup fails.
3. Without a valid RunTable, floserv cannot enter the CommandCentre solve path.
4. floserv falls through to the **translator code path**, which expects a file (not a directory) and tries to open the project directory name as if it were a filename with the GUID as a file extension.
5. The translator fails with E/11029 ("No reader for this file type") and creates a 1×1 empty grid (E/9012).

### What was tested

| Variable | Tested values | Outcome |
|---|---|---|
| Project name format | Full GUID dir, short name, GUID only | All fail identically |
| `group.cat` registration | Registered, unregistered | No difference |
| `ccstatefile.txt` | Present (content "2"), absent | No difference |
| `SALT_LICENSE_SERVER` | `29000@hostname`, `1055@localhost`, unset | No difference |
| `LM_LICENSE_FILE` | `1055@localhost`, unset | No difference |
| `FLOUSERDIR` | Default flouser, clean temp dir | No difference |
| Project | Mobile_Demo, SuperPosition, DefaultSI | All fail identically |
| Existing GUI running | Yes, no | No difference |

### What works instead

#### Direct translator + solver — WORKING HEADLESS (2026-04-12)

The RunTable bug is in **floserv**, not in the actual translator or solver executables. By calling them directly, we bypass floserv entirely and get a fully headless batch solve from SSH:

```
# Step 1: Set up Flotherm environment (without launching floserv)
call "C:\Program Files\Siemens\SimcenterFlotherm\2504\WinXP\bin\flotherm.bat" -env

# Step 2: Translate model to solver format
translator.exe -p "<FLOUSERDIR>\<ProjectName>.<GUID>" -n1

# Step 3: Run solver
solexe.exe -p "<FLOUSERDIR>\<ProjectName>.<GUID>"
```

**Verified on**: Mobile_Demo_Steady_State (153K cells, 2 domains)  
**Environment**: SSH session to win1 (no interactive desktop, no GUI)  
**Solver output**: 500 iterations, single precision, serial, status 4 (max iterations hit)  
**Solver time**: CPU 1:07, Clock 1:41  
**Evidence**: `logit` shows real residuals, Temperature ~35°C, field files modified in `msp_0/end/`

Key points:
- `flotherm.bat -env` sets environment variables without launching anything
- `translator.exe -p <project_path> -n1` translates the model (writes grid, field init files)
- `solexe.exe -p <project_path>` runs the CFD solver directly (writes `logit`, updates `end/` fields)
- Exit codes: both return 0 on success
- `solexed.exe` is the double-precision variant; `solexe_p.exe` is parallel
- No license issues — the SALT/MGLS license is checked at solve time, works from SSH
- Solver log is written to `DataSets/BaseSolution/PDTemp/logit`

This approach does NOT require:
- floserv.exe (bypassed entirely)
- CommandCentre (bypassed)
- RunTable / server.cfg parsing (bypassed)
- Interactive desktop / GUI session
- pywinauto or any GUI automation

`server.cfg` reveals the full invocation chain that floserv normally uses:
```
7 floproxy channel translator -c -p path -nX
10 floproxy channel solexe precision -p path t n -cc scenario
```

#### GUI automation — WORKING (2026-04-11)

Flotherm does not expose an external API, but **GUI automation via pywinauto UIA is proven working**:

```
pywinauto UIA: expand() Macro MenuItem → invoke() Play FloSCRIPT
  (invoke blocks due to modal dialog — run in subprocess with timeout)
Win32 ctypes: fill file dialog (control ID 1148) → click Open (IDOK)
  (standard Windows dialog, not Qt — ctypes works fine)
```

Verified end-to-end: connect → import pack → solve (153K cells, converged) → disconnect.

Key requirements:
- `sim serve` must run in an interactive desktop session (not SSH session 0)
- UIA operations must run in a **subprocess** (COM state corrupts after `invoke()` COMError)
- `pywinauto` must be installed in the sim-cli venv (`uv pip install pywinauto`)

See `sim-proj/.claude/skills/gui-automation/SKILL.md` for detailed patterns and gotchas.

### Impact on test cases

- **EX-01 through EX-04, EX-06, EX-07**: Not affected (don't require actual solve)
- **EX-05**: Documents this failure as a regression baseline
- **Any test requiring actual CFD solve output**: Blocked until GUI automation or batch fix is available

### Misleading exit_code=0

The batch mode returns `exit_code=0` even though the solve never ran. The only reliable indicators of actual solve execution are:
1. **Field file modification**: `DataSets/BaseSolution/msp_*/end/Temperature` timestamp changes
2. **Absence of E/11029 in `floerror.log`**: Written to `FLOUSERDIR/floerror.log`, NOT to stderr
3. **Duration**: A real CFD solve takes >5 seconds; the failed batch path takes ~2 seconds

Current stderr (`registerStart runTable exception`) is always present in batch mode and is **not** the error to check — check `floerror.log` instead.

---

## ISSUE-003: FloSCRIPT CLI playback (`-f` flag) broken in Flotherm 2504

**Date discovered**: 2026-04-12  
**Severity**: High — blocks headless model creation/modification  
**Status**: Open — vendor regression, no workaround except GUI automation

### Symptom

The FloSCRIPTv11 tutorial (shipped at `examples/FloSCRIPT/Tutorial/FloSCRIPTv11-Tutorial.pdf`) documents command-line FloSCRIPT playback:

> FloSCRIPT play back can be initiated from the command line. The appropriate command is: `flotherm.bat -f [FloSCRIPT File]`

In Flotherm 2504, this is silently ignored at every level tested:

| Invocation | Result |
|---|---|
| `flotherm.bat -f script.xml` | GUI opens, script ignored |
| `flotherm.exe -f script.xml` (direct, clean env, no wrapper) | Process runs, creates default `DefaultSI.*` project as if no args passed. `<project_save_as project_name="TestFloScript_001">` did not execute. |
| `floserv.exe 16 -d DefaultSI -f script.xml` | Process runs, no output, no new project in `flouser/` |

The `-f` flag is **not rejected** (no error) and **not honored** (script never runs). It's dropped by the argument parser.

### Evidence

Test FloSCRIPT (`C:\temp\test_script.xml`):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<xml_log_file version="1.0">
    <select_geometry>
        <selected_geometry_name>
            <geometry name="Root Assembly"/>
        </selected_geometry_name>
    </select_geometry>
    <create_geometry geometry_type="cuboid">
        <source_geometry>
            <geometry name="Root Assembly"/>
        </source_geometry>
    </create_geometry>
    <project_save_as project_name="TestFloScript_001" project_title="FloSCRIPT test"
                     save_with_results="false" solution_directory="C:\temp\floscript_test"/>
</xml_log_file>
```

Expected: a project named `TestFloScript_001` appears in `FLOUSERDIR` or at the specified `solution_directory`.  
Observed: only a fresh `DefaultSI.*` project in `FLOUSERDIR` (Flotherm's normal default-on-startup behavior). No `TestFloScript_001` anywhere.

### Pattern: vendor regression

This is the **same regression pattern** as ISSUE-001 (the `-b` flag). Both flags were documented as working in v11 (2015), both are silently dropped in 2504 (2025). The underlying code paths (`floscript.dll`, `floscriptmodel.dll`) still exist in `WinXP/bin/` but are no longer wired to CLI argument handling.

### What works instead

**For FloSCRIPT playback**: GUI automation via pywinauto UIA clicking `Macro → Play FloSCRIPT` (see ISSUE-001 workaround section). This is slow but reliable.

**For model re-solves without parameter changes**: Direct `translator.exe` + `solexe.exe` (ISSUE-001 workaround). Doesn't need FloSCRIPT at all.

**For declarative project creation** (partial, unfinished investigation):
- FloXML `<xml_case>` is a declarative project description (not a command log like FloSCRIPT)
- `flogate_cl -iFloXML -r<file.xml> -oPDML -w<file.pdml>` converts FloXML → Flotherm's internal PDML binary format (**verified working**)
- `floimport.exe -d <dir> <file.pdml>` creates a project directory shell from PDML (**verified working**)
- `flopdupdate + floupdateall -o + flocatalogue -u` populates `DataSets/` and `PDTemp/` scaffolding (**verified**)
- **BLOCKER**: `translator.exe` silently no-ops on the resulting project — the `DataSets/BaseSolution/msp_0/` tree that Mobile_Demo has is never created by this pipeline
- Hypothesis: when the GUI opens a project for the first time, it does internal bootstrap work that creates `BaseSolution/`, and none of the CLI tools replicate that step

This FloXML path is documented fully in `sim-proj/dev-docs/flotherm/resources.md`. Unfinished experiments to try: overlay a working project's scaffolding, reverse-engineer `PDProject/group` binary, or find a FloXML export command in the schemas for round-tripping.

### Recommendation to Siemens

File a bug report citing the FloSCRIPTv11 tutorial PDF (shipped in the install) as documentation that `-f` was supposed to work. Both `-b` and `-f` are regressions — restoring them would unlock headless automation without any new feature work.

---

## ISSUE-002: `sim lint` fails on .pack files via CLI (pybamm detect UnicodeDecodeError)

**Date discovered**: 2026-04-01  
**Severity**: Low — workaround available  
**Status**: Open — cannot fix (pybamm.py is a protected core file)  

### Symptom

`sim lint Mobile_Demo.pack` via CLI crashes because `pybamm` driver's `detect()` calls `read_text()` on the binary .pack file, causing `UnicodeDecodeError`.

### Workaround

Call `FlothermDriver().lint()` directly from Python instead of using the CLI:
```python
from sim.drivers.flotherm.driver import FlothermDriver
result = FlothermDriver().lint(Path("my_project.pack"))
```

Or use `--solver flotherm` to skip auto-detection:
```bash
sim lint --solver flotherm my_project.pack
```
