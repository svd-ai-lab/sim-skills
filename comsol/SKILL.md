---
name: comsol-sim
description: Use when driving COMSOL Multiphysics through the sim runtime — building geometry, materials, physics, mesh, and solving via the JPype Java API, optionally with a human watching the COMSOL GUI client. Includes verification utilities to compensate for broken Windows image export.
---

# comsol-sim

You are driving **COMSOL Multiphysics** via sim-cli in a **persistent
session** (JPype Java API). This file is the **index** — it tells you
where to look for content, not what the content says.

> **First, read [`../sim-cli/SKILL.md`](../sim-cli/SKILL.md)** — it owns
> the shared runtime contract (session lifecycle, Step-0 version probe,
> input classification, acceptance, escalation). This skill covers only
> the COMSOL-specific layer on top of that contract.

---

## COMSOL-specific layered content

After `sim connect --solver comsol` and the shared-skill Step-0 probe,
the returned `session.versions` payload tells you which COMSOL-specific
subfolders to load:

```json
"session.versions": {
  "profile":             "mph_1_2_comsol_6_4",
  "active_sdk_layer":    null,        // single SDK line (mph 1.x), no overlay
  "active_solver_layer": "6.4"        // or "6.2" / "6.1" / "6.0"
}
```

There is no `sdk/` overlay because all supported COMSOL versions pin a
single `mph` line (1.2.x). Always read `base/`, then your active
`solver/<slug>/`.

### `base/` — always relevant

| Path | What's there |
|---|---|
| `base/workflows/block_with_hole/` | Steady-state thermal of a heated block with a cylindrical hole. 6 numbered Python steps (`00_create_geometry.py` … `05_plot_temperature.py`). The canonical "smallest end-to-end" reference for this driver. |
| `base/workflows/surface_mount_package/` | More realistic SMD package thermal model. 6 numbered steps + a `README.md` describing the geometry and acceptance criteria. |

Each numbered step is a self-contained snippet you submit via
`sim exec` after `sim connect --solver comsol`. The snippets use the
injected `model` object — they do NOT call `mph.start()` or open a
client of their own.

### `solver/<active_solver_layer>/` — release specifics

Empty stubs by default; per-release deltas land here as discovered.

- `solver/6.4/notes.md` — current
- `solver/6.2/notes.md`
- `solver/6.1/notes.md`
- `solver/6.0/notes.md`

### `doc-search/` — local documentation lookup

When a physics feature name, API method, or module capability is unknown,
do **not** guess. Query the local COMSOL documentation that ships with
every install:

```bash
uv run --project <sim-skills>/comsol/doc-search sim-comsol-doc search "<term>" [--module <substring>]
```

One-time setup on any host that has COMSOL installed:

```bash
cd <sim-skills>/comsol/doc-search && uv sync
```

(No index build step — each query scans the doc tree in parallel; typical
latency is 1–3 s on a local SSD.)

Tips for good queries:
- Use **2–3 keywords**, not questions. COMSOL search is keyword-matched.
- Filter by `--module battery` / `--heat` / `--cfd` / `--plasma` to bias
  toward a module's plugin folder (matched as a substring of the
  `com.comsol.help.*` name).
- Progressive broadening: if `"C-rate battery"` returns nothing, try
  `"discharge rate"`, then `"battery performance"`.
- For **API / coding** questions, filter `--module programming` or
  `--module api`. Plugin names follow `com.comsol.help.*` — inspect a
  few results and adjust.

To read the full text of a hit:

```bash
uv run sim-comsol-doc retrieve com.comsol.help.battery/battery_aging.03.01.html
```

See `doc-search/README.md` for discovery details and the install-root
override (`--comsol-root`) if auto-detection fails.

#### Application Gallery: local vs. web

The local index also covers the **Application Gallery** content for every
module the user has installed — those plugins are named
`com.comsol.help.models.*` (e.g. `com.comsol.help.models.battery.li_battery_1d`).
Filter with `--module models` to scope a search to example-model docs:

```bash
uv run sim-comsol-doc search "thermal runaway" --module models.battery
```

For models that belong to **modules not installed** on the user's host
(or for browsing by image/category), point the user at
<https://www.comsol.com/models>. Don't scrape it from the skill — just
link.

---

## COMSOL-specific hard constraints

These add to — do not replace — the shared skill's hard constraints.

1. **Never call `mph.start()` or `client.create()` from a snippet.**
   sim-cli already started a COMSOL JVM and gave you a `model` handle.
   A second `start()` spawns a conflicting JVM.
2. **Image export is broken on Windows.** Use the verification helpers
   referenced in the workflow READMEs (slice / probe extraction →
   numeric acceptance) instead of `model.result().export()` PNGs. The
   shared skill's `acceptance.md` explains why numeric acceptance
   beats visual acceptance anyway.

---

## Required protocol (one paragraph)

Follow the shared skill's required protocol for the **persistent
session** model. COMSOL-specific steps: after `sim connect --solver
comsol` and the Step-0 probe, pick a workflow under `base/workflows/`
whose geometry and physics match the user's task, then execute its
numbered snippets in order via `sim exec`, checking `sim inspect
last.result` after each step for `ok=true`. After the final step,
evaluate against the workflow's acceptance criteria (typically a probe
value with a tolerance) per the shared skill's `acceptance.md`.
