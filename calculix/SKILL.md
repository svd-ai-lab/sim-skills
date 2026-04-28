---
name: calculix-sim
description: Use when driving CalculiX (CCX) via Abaqus-style .inp input decks — open-source static/frequency/thermal FEA through sim runtime one-shot execution.
---

# calculix-sim

You are connected to **CalculiX (CCX)** via sim-cli. This file is the
**index**. It tells you where to look for actual content — it does not
contain the content itself.

CalculiX is an open-source finite element solver by Guido Dhondt. It
reads Abaqus-dialect `.inp` input decks and writes results to `.frd`
(field) and `.dat` (text tables via `*NODE PRINT` / `*EL PRINT`).
Execution is pure subprocess: `ccx <jobname>` (no `.inp` extension).

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/inp_keywords.md` | CalculiX-supported `*KEYWORD` list — what works, what's Abaqus-only. |
| `base/reference/analysis_types.md` | Static / Frequency / Thermal / Coupled procedures. |
| `base/reference/result_files.md` | `.frd` and `.dat` format; how to extract numeric results. |
| `base/snippets/01_cantilever_beam.inp` | Verified cantilever beam E2E snippet (B32R beams). |
| `base/known_issues.md` | Quirks discovered during TDD (LD_LIBRARY_PATH, glibc compat). |

## solver/2.11/ — CalculiX 2.11 specifics

- `solver/2.11/notes.md` — Debian buster build, spooles dep, glibc limits.

---

## Hard constraints

1. **`ccx` takes the jobname without extension.** `ccx beam`, NOT `ccx beam.inp`.
2. **Not all Abaqus keywords are supported.** Before inventing a keyword,
   check `base/reference/inp_keywords.md` — if it's not listed, don't use it.
3. **Acceptance != exit code.** Validate against physics (displacement,
   stress, frequency ranges), not just "Job finished".
4. **Output requires explicit keywords.** Without `*NODE FILE` / `*EL FILE`
   the `.frd` is empty; without `*NODE PRINT` / `*EL PRINT` the `.dat` is empty.
5. **LD_LIBRARY_PATH may be required** — the driver sets this automatically
   when the deb-package layout is detected.

---

## Required protocol

After `sim check calculix` confirms availability: gather Category A
inputs from user (geometry, materials, BCs, loads, analysis type,
acceptance criteria). Write the `.inp` deck using only CalculiX-supported
keywords. Lint with `sim lint`. Run with `sim run --solver calculix`.
Parse `.dat` (preferred for numeric extraction) or `.frd` for results.
Validate against physics-based acceptance.
