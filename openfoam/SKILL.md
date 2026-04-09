---
name: openfoam-sim
description: Use when running OpenFOAM cases through the sim runtime on a Linux box — meshing, decompose / mpirun / reconstruct, MPI parallel execution, classifying results PASS/SLOW_PASS/FAIL_*, and recovering from common failure modes via SSH-tunneled `sim connect`/`sim exec`.
---

# openfoam-sim

You are connected to **OpenFOAM** via sim-cli. This file is the **index**.
It tells you where to look for actual content — it does not contain the
content itself.

The `/connect` response told you which active layer applies via:

```json
"skills": {
  "root":               "<sim-skills>/openfoam",
  "active_sdk_layer":   null,        // OpenFOAM has no Python SDK
  "active_solver_layer":"v2406"      // or "v2312" / "v2206"
}
```

Always read `base/`, then your active `solver/<version>/`. There is no
`sdk/` overlay because OpenFOAM has no Python wrapper — the "SDK" is
the bashrc that the inline driver sources at connect time.

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/success_patterns.md` | Distilled from 343 tutorials (105 serial + 238 parallel): what a clean meshing / solver / parallel run looks like. |
| `base/reference/failure_patterns.md` | The recurring failure modes (decomposeParDict mismatch, missing controlDict keys, divergence, etc.) and how to recover. |
| `base/docs/` | Tutorial test plan, runner v2 notes, parallel/serial result tables. Read when you need historical context for an unusual case. |

## solver/<active_solver_layer>/ — release specifics

Empty stubs by default; per-release deltas land here as discovered.

- `solver/v2406/notes.md` — June 2024, current
- `solver/v2312/notes.md` — December 2023
- `solver/v2206/notes.md` — the line the original 343-tutorial suite ran on

## tests/ (top-level, not part of the layered tree)

QA artifacts for the skill itself: `tests/test_driver.py` plus
`tests/fixtures/` (a tiny cavity setup, an empty .foam file, a
hello-world Python script). Not loaded during a normal session.

---

## Hard constraints

1. **OpenFOAM is bash + binaries, not Python.** Every `sim exec` payload
   for OpenFOAM is a shell snippet, not Python code. The driver runs it
   under a bash subshell with the bashrc-sourced env.
2. **Run on the Linux box.** sim-cli's openfoam driver only works when
   `sim serve` is running on the host that has OpenFOAM. Connect from
   your laptop via `sim --host <ip> connect --solver openfoam` (over
   Tailscale or SSH tunnel).
3. **Acceptance ≠ exit code.** A solver that converges to garbage exits
   0. Validate against the case's expected residual / monitor output
   from `base/reference/success_patterns.md`.

---

## Required protocol (one paragraph)

After `/connect` succeeds, run a sanity probe (`sim exec "echo
$WM_PROJECT_VERSION; which simpleFoam"` etc), then execute the case's
Allmesh / Allrun shells incrementally — checking each step's exit code
and tail of the log against `base/reference/success_patterns.md` before
moving on. If a step fails, classify it via the table in
`base/reference/failure_patterns.md` before retrying.
