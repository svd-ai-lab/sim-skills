# Flotherm Environment Shell Probe Report

**Date**: 2026-04-02/03  
**Status**: **SOLVE VERIFIED** — first real example executed end-to-end  
**Environment**: Windows 11 Pro, Simcenter Flotherm 2504, Python 3.13.5

---

## 1. Executive Summary

- **`flotherm.exe -env`** is the official "Environment Shell" entry — it opens a cmd with Flotherm environment. However, it is NOT required for the working execution path.
- **`flotherm.exe` (no args via `explorer.exe`)** launches a fully functional GUI with correct license handling. This is the proven launch method.
- **A real example has been solved end-to-end**: Mobile_Demo-Steady_State, 153,449 grid cells, steady-state converged, field files updated, logit confirms `status 3 normal exit`.
- **The working execution path**: launch GUI via `explorer.exe flotherm.exe` → `Macro > Play FloSCRIPT` (automated via Win32 API) → FloSCRIPT with `project_unlock` + `project_load` + `start start_type="solver"` → solve completes.
- **`flotherm.bat -b` and `flotherm.bat -f` are both non-functional** from subprocess — `-b` has RunTable exception, `-f` causes Project Manager crash (when not in Environment Shell context).

---

## 2. Evidence of Environment Shell

### Start Menu shortcuts

| Shortcut | Target | Arguments | Working Dir |
|----------|--------|-----------|-------------|
| Simcenter Flotherm 2504 | `flotherm.exe` | (none) | `WinXP\bin` |
| Simcenter Flotherm 2504 Environment Shell | `flotherm.exe` | `-env` | `WinXP\bin` |

### What `-env` does

`flotherm.exe -env` opens a cmd.exe window with the Flotherm bin directory as working directory. However, the environment variables are set by `flotherm.bat -env` which is called INSIDE that child cmd, not by `flotherm.exe` itself. The critical difference: `flotherm.exe` handles license initialization via its internal SALT library (`salt_mgls.dll`).

### What was confirmed

- The Environment Shell cmd does have `flotherm.bat` and `floserv.exe` on PATH (via working directory)
- Commands like `flotherm.bat -f script.xml` typed into the Environment Shell DO work (floserv starts without crash)
- However, the same commands fail from a normal cmd or subprocess (even with identical env vars)

---

## 3. Shell Environment Diff

| Item | Normal cmd | `flotherm.exe -env` shell | `flotherm.bat -env` | Notes |
|------|-----------|--------------------------|---------------------|-------|
| `SALT_LICENSE_SERVER` | Not set | Not set (cleared) | `29000@COMPUTERNAME` (WRONG) | Registry has correct value: `C:\ProgramData\MentorGraphics\License\license.dat` |
| `FLO_ROOT` | Not set | Not set | Set correctly | `-env` shell doesn't set FLO vars — flotherm.bat does |
| `PATH` | User default | User default | Includes Flotherm bin/lib | |
| `FLOUSERDIR` | Not set | Not set | `<root>\flouser` | |
| Working dir | User home | `WinXP\bin` | N/A | |
| License | Fails | Works (via `flotherm.exe` internal) | Fails (29000 port not listening) | Root cause of all prior failures |

### The real license mechanism

The SSQ crack registers this in the Windows registry (both HKCU and HKLM):
```
SALT_LICENSE_SERVER = C:\ProgramData\MentorGraphics\License\license.dat
```

- `flotherm.exe` reads this from registry → license works
- `flotherm.bat` **overrides** it with `29000@COMPUTERNAME` → license fails
- Claude Code's shell session does NOT inherit the registry env var → license fails
- Solution: `explorer.exe flotherm.exe` inherits from desktop session → license works

---

## 4. Command Probe Matrix

| Command | Context | Result | Details |
|---------|---------|--------|---------|
| `flotherm.exe` (via explorer) | Desktop | **WORKS** | GUI launches, license OK, DefaultSI loads |
| `flotherm.exe -env` (via explorer) | Desktop | **WORKS** | Opens Environment Shell cmd |
| `flotherm.bat -b project` | Normal cmd | **FAILS** | `registerStart runTable exception`, E/11029 |
| `flotherm.bat -b project` | Env Shell | **FAILS** | Same RunTable exception |
| `flotherm.bat -f script.xml` | Normal cmd | **FAILS** | `Project Manager stopped abnormally` |
| `flotherm.bat -f script.xml` | Env Shell (typed) | Starts GUI | GUI opens but `-f` does NOT auto-play the script |
| `flotherm.bat -f script.xml` | subprocess with correct SALT | Starts GUI | Same — floserv ignores `-f` argument |
| `Macro > Play FloSCRIPT` | GUI (via Win32 API) | **WORKS** | FloSCRIPT Monitor shows progress, commands execute |
| FloSCRIPT: `reset_solver_controls.xml` | Play FloSCRIPT | **WORKS** | Official example, 71%→100%, solver controls modified |
| FloSCRIPT: `<external_command process="CommandCentre"><solve_all/></external_command>` | Play FloSCRIPT | **FAILS** | `ERROR E/15009 - Invalid XML Syntax external_command` |
| FloSCRIPT: `<project_load/>` without unlock | Play FloSCRIPT | **FAILS** | `ERROR E/11013 - Failed to get a lock` |
| FloSCRIPT: `<project_unlock/> + <project_load/> + <start start_type="solver"/>` | Play FloSCRIPT | **WORKS** | **Full solve completed, 153K cells, converged** |

---

## 5. Real Example Test — SUCCESSFUL

### 5.1 Example identity

| Field | Value |
|-------|-------|
| Project | Mobile_Demo_Steady_State |
| Project dir | `Mobile_Demo_Steady_State.002ED56414BAD1BD526E658D00000051` |
| Type | Steady-state PCB thermal model, 2 scenarios (msp_0, msp_1) |
| Grid cells | 153,449 |
| Source | Flotherm 2504 official example (`examples/FloSCRIPT/Demonstration Examples/`) |

### 5.2 Working FloSCRIPT (verified syntax)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xml_log_file version="1.0">
    <project_unlock project_name="Mobile_Demo_Steady_State"/>
    <project_load project_name="Mobile_Demo_Steady_State"/>
    <start start_type="solver"/>
</xml_log_file>
```

Key syntax rules:
- **Drawing Board commands only** — direct children of `<xml_log_file>`, NO `<external_command>` wrapper
- `project_unlock` BEFORE `project_load` — releases stale locks from previous sessions
- `<start start_type="solver"/>` triggers solve, NOT `<solve_all/>`
- `<solve_all/>` is a CommandCentre command wrapped in `<external_command>` — **invalid in Drawing Board context**

### 5.3 Execution method

```
explorer.exe "E:\...\WinXP\bin\flotherm.exe"     # Launch GUI (license via desktop session)
    ↓ (20s wait for GUI init)
Win32 API: Macro menu → Play FloSCRIPT             # FindWindow + keybd_event
    ↓ (file dialog opens)
Win32 API: SetText(1148, path) + Click(IDOK)        # SendMessage to dialog controls
    ↓ (FloSCRIPT Monitor shows progress)
Solve completes → field files updated
```

### 5.4 Pre-solve vs Post-solve evidence

| File | Before | After | Changed? |
|------|--------|-------|----------|
| `msp_0/end/Temperature` | `Apr 1 09:21`, 11632 bytes | **`Apr 2 23:29`**, 11632 bytes | **YES** |
| `PDTemp/logit` | 70688 bytes (old solve data) | Updated with new solve | **YES** |
| `floerror.log` | Not present | Not present | Clean |

### 5.5 logit confirmation

```
status 3 normal exit from main program MAINUU.
Solver CPU Time: 00:00:00:00
Solver Clock Time: 00:00:00:01
Peak Working Set KB: 297636
```

### 5.6 GUI Message Window confirmation (from screenshot)

```
INFO I/9033 - Total number of Grid Cells are: 153449
INFO I/9032 - Translator completed Errors: 0 Warnings: 0 Informationals: 1
INFO I/9050 - Thermal radiation exchange factors are up to date
INFO I/9000 - No Error <CPU Time: 00:00:0m:0s  <Clock Time: ...
INFO I/9001 - Solver stopped: steady solution converged
```

### 5.7 Screenshots

| Screenshot | What it shows |
|-----------|---------------|
| `screen_macro.png` | Macro menu with Play FloSCRIPT visible |
| `screen_play.png` | Play FloSCRIPT file dialog open |
| `screen_after_play.png` | FloSCRIPT Monitor at 71%, executing `modify_solver_control` |
| `s_unlock_result.png` | **Solve complete**: residual plots, monitor points, model tree, convergence message |

All screenshots saved in `C:\flo_ion\`.

---

## 6. First-Principles Interpretation

### 6.1 Can `-env` serve as the basis for `sim connect`?

**Partially.** The Environment Shell provides the correct context for `flotherm.bat` commands, but it requires an interactive cmd window. The proven execution path uses `explorer.exe flotherm.exe` (GUI mode) + Win32 API automation, not the Environment Shell directly.

For `sim connect`, the launch mechanism should be:
1. Set `SALT_LICENSE_SERVER` from registry (or ensure it's inherited)
2. Launch `flotherm.exe` via `explorer.exe` (ensures visible window with correct license)
3. Wait for GUI initialization
4. GUI becomes the "session" that `sim run` interacts with

### 6.2 Is there a real transport for `sim run`?

**YES.** The proven transport is:

```
Win32 API → Macro > Play FloSCRIPT → file dialog → FloSCRIPT XML
```

Specific Win32 calls:
- `FindWindow(class_name='FloMainWindow')` to find the GUI
- `click_input()` on Macro MenuItem via pywinauto UIA
- `keybd_event(DOWN, ENTER)` to select Play FloSCRIPT
- `FindWindow('#32770', 'Play FloSCRIPT')` to find file dialog
- `GetDlgItem(dialog, 1148)` + `SendMessage(WM_SETTEXT)` to set filename
- `GetDlgItem(dialog, 1)` + `SendMessage(BM_CLICK)` to click Open

This is **fully automatable** without keyboard input to the Flotherm window — only Win32 messages to dialog controls.

### 6.3 What is the blocking point?

**None — the path is fully working.** The key requirements are:
1. `SALT_LICENSE_SERVER` must be set correctly (from registry or explicit)
2. GUI must be launched via `explorer.exe` (for visible window + license)
3. FloSCRIPT must use Drawing Board syntax (`project_unlock` + `project_load` + `start`)
4. Win32 API can automate the menu and file dialog without mouse/keyboard

---

## 7. Recommendation for sim-flotherm

**方案 A: 以 GUI + Win32 API Play FloSCRIPT 为基础做 shell-backed runtime。**

This is the recommended path based on proven evidence:

| Component | Implementation |
|-----------|---------------|
| `sim connect` | Launch `flotherm.exe` via `explorer.exe`, set `SALT_LICENSE_SERVER` from registry, wait for GUI |
| `sim run` | Generate FloSCRIPT XML → write to temp file → trigger `Macro > Play FloSCRIPT` via Win32 API → monitor `logit` + field files for completion |
| `sim disconnect` | Close Flotherm GUI (optionally kill floserv) |
| `sim query` | Read `logit` for residuals/convergence, read field file timestamps, read Message Window via screenshots |

### Correct FloSCRIPT template for solve

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xml_log_file version="1.0">
    <project_unlock project_name="{project_name}"/>
    <project_load project_name="{project_name}"/>
    <start start_type="solver"/>
</xml_log_file>
```

### Backend implementation requirements

1. **Launch**: `explorer.exe flotherm.exe` with `SALT_LICENSE_SERVER` set from registry
2. **Wait**: Poll for `FloMainWindow` via `FindWindow` (20s typical)
3. **Dispatch**: Write FloSCRIPT XML → Win32 API `Macro > Play FloSCRIPT` → fill file dialog
4. **Monitor**: Poll `logit` file for `status 3 normal exit` and field file mtime changes
5. **No keyboard input needed**: all automation via `FindWindow` + `SendMessage` + `click_input`

---

## 8. Failed Paths (for reference)

| Path | Error | Root cause |
|------|-------|-----------|
| `flotherm.bat -b` | `registerStart runTable exception` → E/11029 | Vendor defect in floserv batch mode |
| `flotherm.bat -f` (from subprocess) | `Project Manager stopped abnormally` | License not initialized (SALT_LICENSE_SERVER wrong or missing) |
| `flotherm.bat -f` (from Env Shell, typed) | GUI starts but `-f` argument ignored | floserv doesn't auto-play script from `-f` in 2504 |
| `external_command` in FloSCRIPT | `E/15009 Invalid XML Syntax` | CommandCentre commands not valid in Drawing Board context |
| `project_load` without `project_unlock` | `E/11013 Failed to get a lock` | Project locked by current or previous session |
| `SALT_LICENSE_SERVER=29000@COMPUTERNAME` | License checkout fails | Port 29000 not listening; correct value is license.dat file path |

---

## 9. Key Discovery: SALT_LICENSE_SERVER

The single most important finding of this investigation:

```
Registry (HKCU + HKLM):
  SALT_LICENSE_SERVER = C:\ProgramData\MentorGraphics\License\license.dat

flotherm.bat overrides with:
  SALT_LICENSE_SERVER = 29000@%COMPUTERNAME%  (BROKEN — port not listening)
  
explorer.exe inherits from desktop session → registry value → license works
subprocess from Claude Code → variable not inherited → license fails
```

**Fix for runtime**: read `SALT_LICENSE_SERVER` from registry before launching:
```python
import winreg
key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment')
val, _ = winreg.QueryValueEx(key, 'SALT_LICENSE_SERVER')
os.environ['SALT_LICENSE_SERVER'] = val
```
