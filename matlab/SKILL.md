---
name: matlab-sim
description: Use when running MATLAB scripts through the sim runtime — currently one-shot via `sim run --solver matlab`, with persistent local sessions planned for v1. Covers explicit JSON result extraction and conservative handling of MATLAB desktop state.
---

# matlab-sim

You are connected to **MATLAB** via sim-cli. This file is the **index**.
It tells you where to look for actual content — it does not contain the
content itself.

The `/connect` response told you which active layer applies via:

```json
"skills": {
  "root":               "<sim-skills>/matlab",
  "active_sdk_layer":   "24.1",      // or "24.2" / "23.2"
  "active_solver_layer":null         // engine version IS the release pin
}
```

`active_sdk_layer` is the matlabengine package version. There is no
separate `solver/` overlay because each matlabengine X.Y is rigidly
coupled to one MATLAB release (24.1 ↔ R2024a, 24.2 ↔ R2024b, etc.).

Always read `base/`, then your active `sdk/<version>/`. Later layers
override earlier ones on identically-named files.

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/` | MATLAB control patterns: how to pass numpy arrays to engine, how to read engine.workspace, how to surface MATLAB errors as Python exceptions. |
| `base/snippets/` | Ready-made `sim run` payloads for common analyses. |
| `base/workflows/` | End-to-end multi-script examples. |
| `base/driver_upgrade.md` | Process notes for bumping the matlabengine SDK pin. |

## sdk/<active_sdk_layer>/ — engine-version specifics

Empty stubs by default; per-engine deltas land here as discovered.

- `sdk/24.2/notes.md` — matlabengine 24.2 / R2024b
- `sdk/24.1/notes.md` — matlabengine 24.1 / R2024a
- `sdk/23.2/notes.md` — matlabengine 23.2 / R2023b

## tests/ (top-level, not part of the layered tree)

QA artifacts for the skill itself. Not loaded during a normal session.

---

## Hard constraints

1. **MATLAB output is not structured by default.** Always wrap the
   final result in an explicit JSON line on stdout that the driver's
   `parse_output()` can pick up. Free-form `disp()` output gets lost.
2. **Don't leave a MATLAB desktop running.** v0 is one-shot per script;
   the driver tears the engine down between calls. Don't write
   snippets that depend on workspace state surviving across `sim run`
   invocations.

---

## Required protocol (one paragraph)

Validate Category A inputs (the .m script(s), the data files they need,
the acceptance criteria), then `sim run script.m --solver matlab`.
After completion, parse the JSON line off stdout and evaluate against
the user's acceptance criteria. For multi-step pipelines, chain
`sim run` calls — each is its own engine lifecycle.
