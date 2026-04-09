---
name: comsol-sim
description: Use when driving COMSOL Multiphysics through the sim runtime — building geometry, materials, physics, mesh, and solving via the JPype Java API, optionally with a human watching the COMSOL GUI client. Includes verification utilities to compensate for broken Windows image export.
---

# comsol-sim

You are connected to **COMSOL Multiphysics** via sim-cli. This file is
the **index**. It tells you where to look for actual content — it does
not contain the content itself.

The `/connect` response told you which active layer applies via:

```json
"skills": {
  "root":               "<sim-skills>/comsol",
  "active_sdk_layer":   null,        // single SDK line (mph 1.x), no overlay
  "active_solver_layer":"6.4"        // or "6.2" / "6.1" / "6.0"
}
```

Always read `base/`, then your active `solver/<version>/`. There is no
`sdk/` overlay because all supported COMSOL versions pin a single
`mph` line (1.2.x).

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/workflows/block_with_hole/` | Steady-state thermal of a heated block with a cylindrical hole. 6 numbered Python steps (`00_create_geometry.py` … `05_plot_temperature.py`). The canonical "smallest end-to-end" reference for this driver. |
| `base/workflows/surface_mount_package/` | More realistic SMD package thermal model. 6 numbered steps + a `README.md` describing the geometry and acceptance criteria. |

Each numbered step is a self-contained snippet you can submit to
`sim exec` after `sim connect --solver comsol`. The snippets use the
injected `model` object — they do NOT call `mph.start()` or open a
client of their own.

## solver/<active_solver_layer>/ — release specifics

Empty stubs by default; per-release deltas land here as discovered.

- `solver/6.4/notes.md` — current
- `solver/6.2/notes.md`
- `solver/6.1/notes.md`
- `solver/6.0/notes.md`

---

## Hard constraints

1. **Never call `mph.start()` or `client.create()` from a snippet.**
   sim-cli already started a COMSOL JVM and gave you a `model` handle.
   A second `start()` spawns a conflicting JVM.
2. **Image export is broken on Windows.** Use the verification helpers
   referenced in the workflow READMEs (slice/probe extraction → numeric
   acceptance) instead of `model.result().export()` PNGs.
3. **Acceptance ≠ exit code.** Always validate against a numeric
   probe/extract from the relevant workflow's README.

---

## Required protocol (one paragraph)

After `/connect` succeeds, pick a workflow under `base/workflows/` whose
geometry and physics match the user's task, then execute its numbered
snippets in order via `sim exec`, checking `last.result` after each step
for `ok=true`. After the final step, evaluate against the workflow's
acceptance criteria (typically a probe value with a tolerance).
