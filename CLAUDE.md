# CLAUDE.md — for contributors editing sim-skills

**This file is for contributors.** If you are *using* these skills —
driving a solver from your own agent or project — you do not read this
file. The Anthropic skill loader picks up `<solver>/SKILL.md` files by
their YAML frontmatter (`name` + `description`); it does not walk
surrounding `CLAUDE.md` files into an end user's session.

You only see this file if you ran Claude Code from *inside a clone of
sim-skills*. In that case you are almost certainly editing a skill,
adding a new one, or refactoring shared content. The rest of this file
is for that audience.

End-user docs live in [`README.md`](README.md) (the human-facing grid)
and in [`sim-cli/SKILL.md`](sim-cli/SKILL.md) (the agent-facing runtime
contract every driver skill depends on).

---

## What lives where

| Kind of content | Location | Audience |
|---|---|---|
| Shared runtime contract (lifecycle, commands, version probe, acceptance, escalation, input classification) | [`sim-cli/`](sim-cli/SKILL.md) + `sim-cli/reference/*.md` | End users' agents |
| Solver-specific protocol (physics, APIs, quirks per version) | `<solver>/SKILL.md` + `<solver>/{reference,workflows,snippets}/` | End users' agents |
| Human-facing overview, skill grid, news | [`README.md`](README.md) | Humans browsing GitHub |
| Contributor guide (this file) | `CLAUDE.md` | You, right now |

**Rule of thumb while editing:** if a change belongs in more than one
driver, it belongs in `sim-cli/`. If it is solver-specific, it belongs
in `<solver>/`. Never duplicate across drivers.

---

## When editing a skill

1. Keep the YAML frontmatter valid: `name` (letters / numbers / hyphens
   only) and `description` (starts with "Use when…", third person,
   focused on triggering conditions, NOT a workflow summary).
2. Don't move heavy reference content into `SKILL.md` — keep it in
   `reference/` and link.
3. If the change is a shared runtime concern (lifecycle, commands,
   classification, acceptance, escalation, version awareness), edit
   [`sim-cli/`](sim-cli/SKILL.md) instead of the per-driver SKILL.md.
4. Update the `## File index` section of the SKILL.md if you add or
   rename files.
5. Drift between the skill and the driver in
   `../sim-cli/src/sim/drivers/<solver>/` is a bug. Fix one or the
   other; don't leave them disagreeing.

## When adding a new solver skill

1. Create `<new-solver>/SKILL.md` with proper frontmatter.
2. Start by pointing to `../sim-cli/SKILL.md` — the shared contract
   is not repeated. Keep your SKILL.md focused on the solver overlay.
3. Mirror the section structure of an existing pilot
   ([`fluent/SKILL.md`](fluent/SKILL.md),
   [`matlab/SKILL.md`](matlab/SKILL.md),
   [`comsol/SKILL.md`](comsol/SKILL.md)): Identity → Scope → Hard
   constraints → Required protocol → Input validation → File index.
4. Add the matching driver under
   `../sim-cli/src/sim/drivers/<new-solver>/` and register it in
   `../sim-cli/src/sim/drivers/__init__.py`.
5. Add a row to the skill grid in [`README.md`](README.md). (The
   grid lives in README, not here — contributors can link to it.)

## Runtime dependency

These skills control the [`sim`](../sim-cli/) runtime. If you are
developing locally, the runtime repo sits at `../sim-cli/`. See
`../sim-cli/CLAUDE.md` for its internals (driver protocol, registry,
HTTP endpoints). For each solver the matching driver lives at
`../sim-cli/src/sim/drivers/<solver>/`.
