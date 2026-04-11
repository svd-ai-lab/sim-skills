# Known Issues — flotherm-sim

## ISSUE-001: Batch mode (`flotherm.bat -b`) non-functional in Flotherm 2504

**Date discovered**: 2026-04-01  
**Severity**: Critical — blocks all headless solve operations  
**Status**: Open — no workaround within driver layer  

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

The Flotherm **GUI mode** (`floserv.exe 16 -d DefaultSI`) functions correctly:
- Launches CommandCentre + floview via named pipe channels
- Opens projects, runs solves, produces results
- No E/11029, no RunTable errors

### GUI automation — WORKING (2026-04-11)

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
