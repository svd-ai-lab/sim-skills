---
name: sim-cli
description: Use whenever driving any solver through sim-cli — shared session lifecycle, command surface, input classification, version awareness, acceptance, and escalation. Load alongside the solver-specific SKILL.md (fluent-sim, matlab-sim, comsol-sim, …) — this skill owns the runtime contract; the driver skill owns the solver-specific parts.
---

# sim-cli

You are driving a solver through the **sim-cli** runtime. This skill
owns the runtime contract that applies to **every** solver — session
lifecycle, command surface, input validation, version awareness,
acceptance semantics, escalation triggers.

Each driver-specific skill (`fluent-sim`, `matlab-sim`, `comsol-sim`, …)
layers on top of this one. The driver skill owns only:

- Solver-specific hard constraints (e.g. "never call `pyfluent.launch_fluent()`")
- Solver-specific dependency chains (e.g. Fluent meshing `InitializeWorkflow → ImportGeometry → …`)
- Solver-specific artifacts (snippets, workflows, reference, SDK/solver layer notes)

If a rule applies to more than one driver, it belongs here.

---

## How to use this skill

1. Read the driver skill's `SKILL.md` first to learn what solver you're
   driving and which execution model it uses.
2. Read the sections below of **this** skill that match that model.
3. Follow the **Required protocol** at the bottom.

There are two execution models in sim-cli — the driver skill tells you
which one applies:

| Model | Used by | Lifecycle |
|---|---|---|
| **Persistent session** | fluent-sim, comsol-sim, mechanical-sim, mapdl-sim (session mode), workbench-sim, cfx-sim | `connect → exec × N → inspect → disconnect` |
| **One-shot batch** | matlab-sim, starccm-sim, abaqus-sim, pybamm-sim, ansa-sim, flotherm-sim (GUI/FloSCRIPT variant), most OSS solvers | `run → parse_output → evaluate` |

---

## Reference files

| Path | Read when |
|---|---|
| [`reference/command_surface.md`](reference/command_surface.md) | Before writing any `sim …` command — canonical CLI surface, verified against source. |
| [`reference/lifecycle.md`](reference/lifecycle.md) | For the per-step decision loop. Covers both persistent and one-shot models. |
| [`reference/version_awareness.md`](reference/version_awareness.md) | Every session — the mandatory Step-0 version probe and how to pick the right `sdk/` / `solver/` layer inside the driver skill. |
| [`reference/input_classification.md`](reference/input_classification.md) | Before every task — Category A (ask), B (default + disclose), C (file-derive). |
| [`reference/acceptance.md`](reference/acceptance.md) | At the end of every task — outcome-based evaluation. `exit_code == 0` alone is **not** acceptance. |
| [`reference/escalation.md`](reference/escalation.md) | When something goes wrong — what to stop on, what to report. Do not silently retry. |

---

## Hard constraints (apply to every sim-cli session)

1. **Never invent Category A defaults.** Physical decisions (geometry,
   materials, BCs, acceptance criteria) must come from the user. User
   pressure to "just use defaults" does **not** override this. See
   `reference/input_classification.md`.
2. **Step-0 version probe is mandatory.** After `sim connect` succeeds
   (persistent) or before `sim run` (one-shot), call
   `sim --host <host> inspect session.versions` (or the driver's
   documented equivalent) and use the returned `profile` /
   `active_sdk_layer` / `active_solver_layer` to pick the right files
   inside the driver skill. If `profile` is empty, unknown, or
   deprecated — **stop**. See `reference/version_awareness.md`.
3. **Acceptance ≠ exit code.** A `sim run` or `sim exec` can return
   `ok=true` and the simulation can still be physically wrong. Always
   validate against an outcome-based criterion from the driver skill's
   acceptance checklist. See `reference/acceptance.md`.
4. **Never silently retry a failed step.** Report `stderr`, `stdout`,
   and `run_count` / completion state; let the user decide the next
   move. See `reference/escalation.md`.
5. **Reference example values are not defaults.** Values in any
   `.../examples/` directory describe a specific published test case.
   You may offer them ("the mixing_elbow example uses 0.4 m/s — would
   you like to use those values?") but must wait for explicit
   confirmation before adopting them.

---

## Required protocol (one paragraph)

Before any `sim` command: read the driver skill's `SKILL.md` and its
"Required protocol" section. Classify inputs per
`reference/input_classification.md`; ask the user for missing
Category A inputs, including the acceptance criterion. Start the
session (`sim connect` for persistent, nothing for one-shot). Run the
Step-0 version probe (`sim inspect session.versions`) and pick the
driver-skill subfolder that matches the returned profile. Execute per
`reference/lifecycle.md` — incrementally for persistent sessions,
validate-then-run for one-shot. After the final step (or the one-shot
return), evaluate against the driver skill's acceptance checklist per
`reference/acceptance.md`. On any failure, follow
`reference/escalation.md` — do not silently retry.
