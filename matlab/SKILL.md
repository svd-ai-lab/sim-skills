---
name: matlab-sim
description: Use when running MATLAB scripts through the sim runtime — currently one-shot via `sim run --solver matlab`, with persistent local sessions planned for v1. Covers explicit JSON result extraction and conservative handling of MATLAB desktop state.
---

# matlab-sim

You are driving **MATLAB** via sim-cli in the **one-shot batch** model.
This file is the **index** — it tells you where to look for content,
not what the content says.

> **First, read [`../sim-cli/SKILL.md`](../sim-cli/SKILL.md)** — it owns
> the shared runtime contract (command surface, one-shot lifecycle,
> Step-0 version probe, input classification, acceptance, escalation).
> This skill covers only the MATLAB-specific layer on top of that
> contract.

---

## MATLAB-specific layered content

`sim inspect session.versions` (run against a short-lived session
before your real `sim run`) returns:

```json
"session.versions": {
  "profile":             "matlabengine_24_1",  // or 24.2 / 23.2
  "active_sdk_layer":    "24.1",                // matlabengine package version
  "active_solver_layer": null                   // engine version IS the release pin
}
```

`active_sdk_layer` is the matlabengine package version. There is no
separate `solver/` overlay because each matlabengine X.Y is rigidly
coupled to one MATLAB release (24.1 ↔ R2024a, 24.2 ↔ R2024b, …).

Always read `base/`, then your active `sdk/<slug>/`.

### `base/` — always relevant

| Path | What's there |
|---|---|
| `base/reference/` | MATLAB-specific control patterns: how to pass numpy arrays to engine, how to read engine.workspace, how to surface MATLAB errors as Python exceptions. |
| `base/snippets/` | Ready-made `sim run` payloads for common analyses. |
| `base/workflows/` | End-to-end multi-script examples. |
| `base/driver_upgrade.md` | Process notes for bumping the matlabengine SDK pin. |

### `sdk/<active_sdk_layer>/` — engine-version specifics

Empty stubs by default; per-engine deltas land here as discovered.

- `sdk/24.2/notes.md` — matlabengine 24.2 / R2024b
- `sdk/24.1/notes.md` — matlabengine 24.1 / R2024a
- `sdk/23.2/notes.md` — matlabengine 23.2 / R2023b

### Documentation lookup

Primary route for every MATLAB doc question is **MATLAB's own `help()`
/ `doc` via the engine**. The filesystem scanner in `doc-search/` is a
narrow fallback — on R2024+ it finds almost nothing because MathWorks
now ships reference docs as a Lucene binary index, not static HTML.

#### Primary: `help()` / `doc` via the engine

From a live sim session:

```bash
sim exec "disp(help('fft'))"
sim exec "disp(help('ode45'))"
sim exec "disp(help('fmincon'))"        # Optimization Toolbox
sim exec "disp(help('solve'))"          # Symbolic Math Toolbox
```

Without a session (and without paying matlabengine startup cost), use
the MATLAB launcher directly:

```bash
matlab -batch "disp(help('fft'))"
```

This is authoritative — it reflects the toolboxes actually loaded,
respects shadowing, and handles overloaded methods correctly. Works
identically across all MATLAB releases. Verified end-to-end against
R2025b: returns structured syntax + arguments + examples + see-also.

For a longer write-up (the `doc` command's content), use
`sim exec "open(which('fft'));"` only when a desktop is available;
otherwise query the online docs at `https://www.mathworks.com/help/`.

#### Fallback: `sim-matlab-doc` filesystem scanner

**Known limitation:** on MATLAB R2024a and later, the per-toolbox
folders under `<matlabroot>/help/` (`optim/`, `simulink/`, `stats/`,
`signal/`, `control/`, `symbolic/`, …) contain **no HTML reference
pages** — only Lucene binary indexes (`.cfs`/`.cfe`/`.si`) that the
regex scanner can't read. The `matlab/` folder does have ~500 HTML
files, but they're Code Analyzer diagnostics, not function refs.

What the scanner still catches on modern installs:
- `derived/toolbox/learning/…` — Simulink tutorial / learning content.
- Pockets of HTML under `customdoc/`, `coder/`, and a few other dirs.
- The core MATLAB help on **R2023b and earlier** (full static HTML).

If you're on R2023b or older, or you're grepping for tutorial-style
content, it's still useful:

```bash
cd <sim-skills>/matlab/doc-search && uv sync   # one-time install
uv run --project <sim-skills>/matlab/doc-search \
    sim-matlab-doc search "<keywords>" [--module <toolbox>]
```

For any function / API question on R2024+, go straight to `help()`.

### `tests/` (top-level, QA-only)

Not loaded during a normal session.

---

## MATLAB-specific hard constraints

These add to — do not replace — the shared skill's hard constraints.

1. **MATLAB output is not structured by default.** Always wrap the
   final result in an explicit JSON line on stdout that the driver's
   `parse_output()` can pick up. Free-form `disp()` output gets lost —
   the parser only picks up the **last** JSON object in stdout.
2. **Don't depend on workspace survival across calls.** v0 is
   one-shot per script; the driver tears the engine down between
   `sim run` invocations. Do not write snippets whose correctness
   depends on workspace state set by an earlier `sim run`.
3. **No MATLAB desktop.** Driver launches headless. Do not add
   `desktop` / `-desktop` flags — there is no display.

---

## Required protocol (one paragraph)

Follow the shared skill's required protocol for the **one-shot batch**
model. MATLAB-specific steps: validate the `.m` script exists and its
dependencies (data files, toolboxes) are on the MATLAB path; confirm
the final script line emits a structured JSON object on stdout; run
`sim run <script.m> --solver matlab`; parse the JSON line from stdout
(the driver does this via `parse_output()`) and evaluate against the
user's acceptance criterion per the shared skill's `acceptance.md`.
For multi-step pipelines, chain `sim run` calls — each is its own
engine lifecycle with no shared state.
