---
name: ltspice-sim
description: Use when running LTspice circuit simulations through sim-cli — authoring `.net` netlists (and soon `.asc` schematics) for analog, power-electronics, and board-level designs, then reading structured `.meas` results from the log. Covers netlist authoring conventions, platform quirks (macOS 17.x vs Windows 26.x), and the sim-cli one-shot batch lifecycle.
---

# ltspice-sim

You are driving **LTspice** via sim-cli in the **one-shot batch** model.
This file is the **index** — it tells you where to look for content,
not what the content says.

> **First, read [`../sim-cli/SKILL.md`](../sim-cli/SKILL.md)** — it owns
> the shared runtime contract (command surface, one-shot lifecycle,
> Step-0 version probe, input classification, acceptance, escalation).
> This skill covers only the LTspice-specific layer on top of that
> contract.

---

## What LTspice is (and isn't)

LTspice is the free SPICE3 simulator from Analog Devices. It has **no
vendor Python API** — unlike Fluent (pyfluent), COMSOL (mph), or MATLAB
(matlabengine). The sim-cli driver for LTspice is a thin adapter over
[**sim-ltspice**](https://github.com/svd-ai-lab/sim-ltspice), a
standalone Python library that IS the Python API for LTspice.

Implication: everything in this skill stays identical whether you call
`sim run foo.net --solver ltspice`, or import `sim_ltspice` directly in
Python. The file format understanding and platform quirks are the same.

## Input classification

| Input | Accepted by sim-cli? | Notes |
|---|---|---|
| `.net` / `.cir` / `.sp` netlist | ✅ today | SPICE3 syntax; first line is title (ignored by solver); must contain at least one analysis directive |
| `.asc` schematic (flat, library-local) | 🟡 sim-ltspice v0.1+ — on macOS goes through our native asc2net; on Windows/wine goes through LTspice's own `-netlist` | Schematic opens in LTspice GUI for human review |
| `.asc` schematic (hierarchical or custom lib) | 🟡 Windows / wine only | Requires LTspice's own `-netlist` pass; on macOS raises `MacOSCannotFlatten` with guidance to run `sim --host <win1>` |
| `.raw` / `.log` inputs | ❌ outputs only | Do not pass these to `sim run` |

When you produce a netlist for an agent workflow, **always use `.net`**.
It's the most portable (no LTspice version drift) and the sim-cli
driver has the fewest edge cases for it.

## Platform capabilities

| Capability | macOS 17.x native | Windows 26.x | Linux + wine |
|---|---|---|---|
| `-b <netlist>` batch run | ✅ | ✅ | ✅ |
| `-Run -b` | ❌ (ignored) | ✅ | ✅ |
| `-ascii` raw output | ❌ | ✅ | ✅ |
| `-netlist <asc>` schematic→netlist | ❌ | ✅ | ✅ |
| `.asc` direct input to sim run | native asc2net only (flat + library-local) | full | full |
| `.log` encoding | UTF-16 LE (no BOM) | UTF-8 | UTF-16 LE |
| `.raw` header encoding | UTF-16 LE | UTF-16 LE | UTF-16 LE |

If you need a feature Windows has and macOS lacks, route through
`sim --host <win1>`. See `../sim-cli/SKILL.md` for the HTTP dispatch
model.

## Hard constraints (LTspice-specific)

These add to — do not replace — the shared skill's hard constraints.

1. **Every netlist must have an analysis directive.** At least one of
   `.tran`, `.ac`, `.dc`, `.op`, `.noise`, `.tf`, `.four`. Without one,
   LTspice returns exit code 0 but produces no useful output. `sim lint`
   catches this.
2. **Put `.meas` statements in the netlist, not in a config file.**
   That's how structured values get surfaced on `sim logs last --field
   measures`. Free-form `.print` output is harder to parse.
3. **Never rely on workspace / state across `sim run` calls.** Each
   invocation is a cold LTspice batch. Chain steps by writing out
   intermediate `.net` variations in Python, not by stateful execution.
4. **First line of a netlist is the title, always ignored.** Component
   declarations start at line 2. A common mistake is putting `V1 in 0
   1` on line 1 — LTspice silently treats it as comment text.
5. **Use single-letter element prefixes.** `R` / `C` / `L` / `V` / `I`
   / `D` / `Q` / `M` / `X`. Two-letter names like `R1a` are fine as
   *instance labels*, but the first letter must match the element
   kind.
6. **Ground is net `0` (numeric zero).** Not `GND`, not `0v`. Other
   names are arbitrary user-defined nets.

## Required protocol (one paragraph)

Follow the shared skill's required protocol for the **one-shot batch**
model. LTspice-specific steps: validate the `.net` has a title line +
at least one analysis directive + `.meas` statements for every metric
the acceptance criterion checks; run `sim run <script.net> --solver
ltspice`; read the structured results with `sim logs last --field
measures` (returns `{"<name>": {"expr": "...", "value": <float>,
"from": ..., "to": ...}}`); evaluate against acceptance per the shared
skill's `acceptance.md`. For parameter sweeps, use `.step param` inside
the netlist — one `sim run` covers the whole sweep; the resulting
`.raw` has one dataset per step.

## LTspice-specific layered content

Always read `base/reference/`, then the relevant snippets + workflows.

### `base/` — always relevant

| Path | What's there |
|---|---|
| `base/reference/spice_directives.md` | Cheat sheet: `.tran`, `.ac`, `.dc`, `.op`, `.noise`, `.meas`, `.step`, `.param`, `.ic`, `.nodeset`, `.save` |
| `base/reference/element_syntax.md` | R / C / L / V / I / D / Q / M / X instance syntax + common model options |
| `base/reference/result_extraction.md` | Three layers (`.meas` → `RawRead` cursors → arrays) + `eval` / `to_csv` / `to_dataframe`. Read before reaching for `.raw` |
| `base/reference/platform_dispatch.md` | When to use `--host <win1>`; macOS flat-asc-only constraint |
| `base/snippets/rc_lowpass.net` | Minimal RC transient with one `.meas` |
| `base/snippets/rlc_ac.net` | Series-RLC band-pass AC sweep — complex `.raw` traces, resonance `.meas` |
| `base/snippets/inverting_amp.net` | Inverting op-amp with `.include LTC.lib` and gain `.meas` |
| `base/snippets/param_sweep.net` | `.step param R 1k 100k dec 5` + acceptance via `.meas` max/min |
| `base/workflows/meas_based_acceptance.md` | End-to-end: define acceptance → write `.meas` → `sim run` → read JSON → verify |
| `base/workflows/regression_diff.md` | Two-run `.raw` comparison with `sim_ltspice.diff(a, b)`. Pin a golden `.raw`, gate refactor PRs on waveform equivalence |
| `base/workflows/gui_review_handoff.md` | Python builds `.asc` → spawn LTspice GUI → human reviews / edits → re-read. Waveform viewer handoff. `sim.gui` pywinauto notes for Windows dialogs |
| `base/workflows/param_sweep_postprocess.md` | `.step param` sweep → extract per-step scalars (`.meas`) or slice full traces (`RawRead.to_dataframe()` + axis-seam split) for plotting / custom math |
| `base/workflows/monte_carlo.md` *(planned — not yet written)* | Monte-Carlo via `.step` + `mc()` + Python loop with `sim run` per seed |

### Documentation lookup

LTspice ships an extensive offline help set on Windows at
`%LOCALAPPDATA%\Programs\ADI\LTspice\LTspiceHelp\` (~145 HTML files,
comprehensive SPICE + analysis reference). macOS ships no HTML help
(the native app has an in-GUI help only).

For authoritative syntax questions when on Windows:

```bash
sim --host 100.90.110.79 exec 'cat "%LOCALAPPDATA%\Programs\ADI\LTspice\LTspiceHelp\<topic>.html"'
```

For anyone else, consult the LTspice Users' Guide PDF (search
"LTspice Getting Started Guide" — Analog Devices publishes it openly).

### `tests/` (top-level, QA-only)

Not loaded during a normal session. Mirrors the sibling skills'
convention.

---

## Common pitfalls (save yourself a cycle)

1. **Missing ground reference.** Every net that isn't declared somewhere
   must be connected to something — LTspice flags singular matrices
   cryptically. Always add ground (`FLAG 0` via the netlist is
   implicit when you reference net `0`).

2. **`.meas` misspelled as `.measure`.** Both work, but `.meas` is the
   shorter form used in every example and our parser is tuned for it.

3. **Windows `.log` encoding trap.** LTspice 26 writes UTF-8 logs;
   LTspice 17 (macOS) writes UTF-16 LE. `sim-ltspice` handles both
   transparently, but if you're reading the `.log` yourself with
   `open()`, sniff the encoding.

4. **Drive-letter paths in logs.** On Windows, the `.log` has a
   `Files loaded:\nC:\Users\...\design.net` block. A naive regex
   parser would see `C:` as a measure name. If you roll your own
   log parser, exclude newlines from the expression capture. (Ours
   does — see the sim-cli driver's regex.)

5. **macOS `.asc` refusal.** If `sim run my.asc --solver ltspice`
   errors with `MacOSCannotFlatten`, either (a) ensure the schematic
   uses only shipped-library symbols and no hierarchy, or (b) route
   via `sim --host <win1>`.
