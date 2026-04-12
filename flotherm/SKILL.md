---
name: flotherm-sim
description: Use when running Simcenter Flotherm thermal cases through the sim runtime. Two solve paths: (1) direct batch via translator.exe + solexe.exe (headless, no GUI), (2) GUI automation via pywinauto UIA for .pack import.
---

# flotherm-sim

You are connected to **Simcenter Flotherm** via sim-cli. This file is
the **index**. It tells you where to look for actual content — it does
not contain the content itself.

The `/connect` response told you which active layer applies via:

```json
"skills": {
  "root":               "<sim-skills>/flotherm",
  "active_sdk_layer":   null,        // Flotherm has no Python SDK
  "active_solver_layer":"2504"       // or "2412" / "2406"
}
```

Always read `base/`, then your active `solver/<version>/`. There is no
`sdk/` overlay because Flotherm has no Python wrapper — the driver
controls Flotherm via pywinauto UIA (Qt menu automation) + Win32
ctypes (standard file dialogs).

---

## Execution paths

### Direct batch (headless, preferred for re-solves)

Bypasses floserv entirely — calls translator and solver executables directly.
Works from SSH with no interactive desktop.

```batch
call flotherm.bat -env                     # set environment only
translator.exe -p "<FLOUSERDIR>\<project>" -n1   # translate model
solexe.exe -p "<FLOUSERDIR>\<project>"           # run CFD solver
```

**Requirements**: Project must already be unpacked in `FLOUSERDIR` (registered in `group.cat`).
**Solver log**: `<project>/DataSets/BaseSolution/PDTemp/logit`
**Result fields**: `<project>/DataSets/BaseSolution/msp_*/end/Temperature` etc.

### GUI automation (for .pack import + first solve)

```bash
sim connect --solver flotherm --ui-mode gui     # launch Flotherm GUI
sim exec '<path>.pack'                          # import pack into GUI
sim exec 'solve'                                # run CFD solve
sim exec 'status'                               # query session state
sim disconnect                                  # kill all processes
```

### How GUI automation works

```
sim exec → driver.run() → _play_floscript(script_path)
  ├─ subprocess: pywinauto UIA expand() Macro → invoke() Play FloSCRIPT
  │  (invoke blocks due to modal dialog; subprocess killed after timeout)
  └─ main process: Win32 ctypes fills file dialog → clicks Open
```

UIA runs in a **subprocess** to isolate COM state corruption from the
server process. The file dialog is a standard Windows dialog, handled
via `GetDlgItem(1148)` + `SendMessage(WM_SETTEXT)` + `BM_CLICK`.

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/floscript_modeling.md` | **FloSCRIPT model generation reference** — command vocabulary, patterns, step templates for building models from scratch via Claude. |
| `base/reference/` | FloSCRIPT XML patterns, GUI control sequences, Win32 message recipes. |
| `base/workflows/` | End-to-end demo runs of typical Phase A `.pack` cases. |
| `base/docs/` | Background on the GUI-automation approach and why headless batch is broken upstream. |
| `base/skill_tests/` | Skill QA cases (kept inside `base/` for flotherm because the GUI playback IS the skill — there's no separate Python control surface). |

## solver/<active_solver_layer>/ — release specifics

Empty stubs by default; per-release deltas land here as discovered.

- `solver/2504/notes.md` — 2025.1, current
- `solver/2412/notes.md` — 2024.4
- `solver/2406/notes.md` — 2024.2

## known_issues.md and tests/ (top-level)

Top-level QA artifacts. `known_issues.md` documents the
vendor-defect-broken headless batch mode. `tests/` is the pytest suite
for the inline driver. Not loaded during a normal session.

---

## Example files provenance

Files under `base/reference/flotherm/2504/examples/` are copies of
vendor-shipped demo models from the Flotherm installation directory:

| Skill path | Source (Flotherm install) |
|---|---|
| `examples/pack/Mobile_Demo-Steady_State.pack` | `examples\FloSCRIPT\Demonstration Examples\Transient Power Update\Mobile_Demo-Steady_State.pack` |
| `examples/pack/SuperPosition.pack` | `examples\Demonstration Models\Superposition\SuperPosition.pack` |

These can be regenerated from any Flotherm 2504 installation at
`C:\Program Files\Siemens\SimcenterFlotherm\2504\examples\`.

## Model generation (building from scratch)

To build a Flotherm model from a natural language description, generate
FloSCRIPT XML step by step. See `base/reference/floscript_modeling.md`
for the full command reference, common patterns, and pitfalls.

```bash
sim connect --solver flotherm --ui-mode gui
sim lint step1.xml                          # XSD validates automatically
sim exec step1.xml                          # create geometry + save checkpoint
sim lint step2.xml
sim exec step2.xml                          # add sources + save checkpoint
sim exec 'solve'                            # run CFD
sim disconnect
```

Each step is a separate FloSCRIPT file with `<project_save_as>` at the
end for crash recovery. Lint before play — XSD validation catches
typos and structural errors with line numbers.

## Hard constraints

1. **GUI must be visible.** The automation uses pywinauto UIA which
   requires the Flotherm window to be in an interactive desktop session.
   `sim serve` must be started from RDP, not SSH.
2. **Don't open Flotherm by hand while sim is using it.** UIA element
   discovery races with user input. Let the driver own the lifecycle.
3. **UIA must run in a subprocess.** `invoke()` on Qt menu items throws
   COMError and corrupts COM state for the entire process. Always
   isolate in `subprocess.Popen` with timeout.
4. **Acceptance ≠ exit code.** Always extract a numeric (max temp,
   junction-to-ambient ΔT) from the .pack output and validate against
   the user's criterion.

---

## Required protocol

1. `sim connect --solver flotherm --ui-mode gui` — launches Flotherm
2. `sim exec '<path>.pack'` — imports pack (uses `project_import` FloSCRIPT with `import_type="Pack File"`)
3. `sim exec 'solve'` — plays `<start start_type="solver"/>` FloSCRIPT
4. Verify solve completed: check Message Window for `I/9001 - Solver stopped: steady solution converged`
5. `sim disconnect` — kills floserv, floview, flotherm
