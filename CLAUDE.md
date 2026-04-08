# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code under `sim-skills/`.

## What is this directory?

`sim-skills/` is a collection of **per-solver agent skills** for the [`sim`](../sim-cli/) simulation runtime. Each subdirectory (`ansa/`, `comsol/`, `flotherm/`, `fluent/`, `matlab/`, `openfoam/`) is **one skill** in the Anthropic skill format:

```
<solver>/
  SKILL.md         ← required, with YAML frontmatter (name + description)
  <supporting files: reference/, workflows/, snippets/, tests/, docs/, ...>
```

The skills tell an LLM agent **how to drive a given solver through `sim`** — input validation, connect, execute snippets / scripts, verify acceptance, classify success/failure, recover from common errors. They are *runtime control* skills, not general solver tutorials.

## How to use these skills

When a task involves any supported solver:

1. Identify the solver from the user's request
2. Read `<solver>/SKILL.md` — its YAML `description` field describes exactly when it applies, and the body has the required protocol
3. Follow the protocol step by step (input validation → connect → execute → verify → report)
4. Reach for supporting files when SKILL.md instructs: `reference/` for patterns and templates, `workflows/` for end-to-end examples, `snippets/` for ready-made `sim exec` payloads, `skill_tests/` for acceptance test cases
5. **Never invent solver-specific defaults for Category A (physical-decision) inputs** — ask the user

## The 6 skills

| Directory | Skill name | Use when |
|---|---|---|
| `ansa/` | `ansa-sim` | Running BETA CAE ANSA v25 pre-processor scripts in headless batch (Phase 1; no persistent session, no GUI) |
| `comsol/` | `comsol-sim` | Driving COMSOL Multiphysics via the JPype Java API, with optional human GUI oversight |
| `flotherm/` | `flotherm-sim` | Running Simcenter Flotherm 2504 thermal `.pack` cases via GUI + Win32 FloSCRIPT playback (Phase A) |
| `fluent/` | `fluent-sim` | Driving an Ansys Fluent meshing or solver session via PyFluent 0.38 — incremental snippets or single-file workflows |
| `matlab/` | `matlab-sim` | Running MATLAB `.m` scripts one-shot via `sim run --solver matlab` (v0); persistent sessions planned for v1 |
| `openfoam/` | `openfoam-sim` | Running OpenFOAM v2206 cases through `sim serve` on a Linux box via SSH tunnel — meshing, MPI parallel, classifier-based pass/fail |

## Cross-skill conventions

These conventions apply across all 6 skills. Each individual SKILL.md may add its own constraints on top.

### Input classification (used in every skill's "Required protocol" Step 1)

- **Category A — Physical decision inputs:** must ask the user if absent. These define what the simulation physically represents (geometry, materials, boundary conditions, acceptance criteria). User pressure to "just use defaults" does NOT override this.
- **Category B — Operational inputs:** may default, must disclose. These affect runtime/performance only (processors, ui_mode, smoke-test iteration counts).
- **Category C — File-derivable:** infer from the actual provided files via a diagnostic snippet, not from reference examples. Confirm with the user if critical.

### Acceptance criteria are required inputs

For every skill: `exit_code == 0` ALONE does **not** satisfy acceptance. Always validate against an outcome-based criterion ("outlet temperature in 28–35°C", "150 iterations completed", "min mesh quality > 0.2"). Phrases like "just run it" / "跑完就好" describe an operation, not an outcome — treat them as a missing input and ask.

### Reference example values are NOT defaults

Values in any `reference/.../examples/` directory describe a specific published test case. They are **not** silently applicable to a different user's task. You may *offer* them ("the mixing_elbow example uses 0.4 m/s — would you like to use those values?") but must wait for explicit confirmation before adopting them as Category A inputs.

### Runtime version awareness (Step 0 of every skill)

**Mandatory.** The first thing every skill protocol does after `sim connect` succeeds is:

```bash
sim --host <ip> inspect session.versions
```

This returns:

```json
{
  "sdk":     {"name": "ansys-fluent-core", "version": "0.38.1"},
  "solver":  {"name": "fluent",            "version": "25.2"},
  "profile": "pyfluent_0_38_modern",
  "skill_revision": "v2",
  "env_path": "/.../.sim/envs/fluent-pyfluent-0-38"
}
```

The agent **must** use the returned `profile` (or `skill_revision`) to choose which subfolder to load:

- **Snippets:** read only from `<skill>/snippets/<profile>/*.py` and `<skill>/snippets/common/*.py`. Never load a snippet from a different profile folder.
- **Reference docs:** anything in `<skill>/reference/<profile>/` overrides anything in `<skill>/reference/common/` for that profile.
- **Workflows:** same profile-folder rule as snippets.

If `profile` is empty, unknown, or marked deprecated in the driver's `compatibility.yaml`, **stop and surface the version table to the user**. Do not guess. The contract for this whole mechanism is in [`sim-cli/docs/architecture/version-compat.md`](https://github.com/svd-ai-lab/sim-cli/blob/main/docs/architecture/version-compat.md).

Why this matters: a snippet written for PyFluent 0.38 (uses `.general.material`) silently produces `AttributeError` on PyFluent 0.37 (which expects `.material` directly). Without Step 0 the agent has no way to tell which dialect it should write — it would have to guess from the SDK version, which is exactly the bug Step 0 fixes.

### When to stop and escalate

Across all skills, stop and report (don't silently retry) when:
- The solver / driver is unavailable or fails to launch
- The runtime profile is empty, unknown, or deprecated (see "Runtime version awareness" above)
- A snippet returns non-zero exit / `ok=false` / raises an exception
- Session state is inconsistent with expectations after a step
- The acceptance checklist cannot be satisfied

## Runtime dependency

These skills are useless without the [`sim`](../sim-cli/) runtime installed. See `../sim-cli/CLAUDE.md` for:
- The dual execution model (one-shot `sim run` vs persistent `sim serve` + `sim connect/exec/inspect`)
- Driver protocol (`DriverProtocol` in `sim.driver`)
- Driver registry (`sim.drivers.__init__`)
- HTTP server endpoints

For each solver, the matching driver lives at `sim-cli/src/sim/drivers/<solver>/`.

## When editing a skill

If you change a `SKILL.md`:

1. Keep the YAML frontmatter valid: `name` (letters / numbers / hyphens only) and `description` (starts with "Use when…", third person, focused on triggering conditions, NOT a workflow summary)
2. Don't move heavy reference content into SKILL.md — keep it in `reference/` and link
3. Update the `## File index` section if you add or rename files
4. The skill is the source of truth for the agent — drift between SKILL.md and the actual driver in `sim-cli/src/sim/drivers/<solver>/` is a bug; fix one or the other

## When adding a new solver skill

1. Create `sim-skills/<new-solver>/SKILL.md` with proper frontmatter
2. Mirror the section structure of the existing skills (Identity → Scope → Hard constraints → Required protocol → Input validation → File index)
3. Add the matching driver under `sim-cli/src/sim/drivers/<new-solver>/` and register it in `sim-cli/src/sim/drivers/__init__.py`
4. Add the new skill to the table in this CLAUDE.md and in `README.md`
