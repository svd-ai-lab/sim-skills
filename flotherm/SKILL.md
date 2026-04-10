---
name: flotherm-sim
description: Use when running Simcenter Flotherm thermal cases through the sim runtime — Phase A `.pack` execution via Win32 API automation playing back FloSCRIPT XML in the Flotherm GUI. Headless batch mode is currently broken (vendor defect).
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
controls Flotherm via Win32 API GUI automation.

---

## base/ — always relevant

| Path | What's there |
|---|---|
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

## Hard constraints

1. **GUI must be visible.** Phase A is GUI automation; running headless
   or in a remote-desktop-disconnected session causes Win32 SendInput
   to no-op silently.
2. **Don't open Flotherm by hand while sim is using it.** Win32 message
   delivery races between user input and the playback. Let the driver
   own the lifecycle.
3. **Acceptance ≠ exit code.** Always extract a numeric (max temp,
   junction-to-ambient ΔT) from the .pack output and validate against
   the user's criterion.

---

## Required protocol (one paragraph)

After `/connect` succeeds, validate Category A inputs (the .pack file,
the FloSCRIPT XML, acceptance criteria), launch the playback through
the driver, and watch for the playback-complete signal. After
completion, parse the .pack result file and evaluate against the
user's acceptance criterion.
