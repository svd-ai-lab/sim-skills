---
name: readme-blueprint-generator
description: Use when the user asks for a polished, eye-catching GitHub README for a software project. Project-local fork for sim-skills — a collection of per-solver agent skills, not a runtime. Specialized for "playbook library" READMEs that pair visually with the sibling sim-cli README.
---

# README Blueprint Generator (sim-skills fork)

Goal: produce a `README.md` that **stops the scroll in 2 seconds** and **earns a star in 30 seconds**, visually paired with the sibling `sim-cli` README.

This repo is a **collection of agent skills**, not a runtime. Content emphasis differs from a typical code README:

- The headline artifact is a **grid of skills**, not a CLI surface
- Per-skill status matters (Phase A, Phase 1, v0, Working) — be honest
- The companion runtime `sim-cli` is always cross-linked in the hero

## Sources (in priority order)

1. `CLAUDE.md` — authoritative on protocol, cross-skill conventions, runtime dependency
2. `<solver>/SKILL.md` YAML frontmatter — name + description of each skill
3. Individual SKILL.md bodies — execution model, phase, gotchas
4. Existing `README.md` — preserve good wording, do not regress
5. Sibling `sim-cli` repo — cross-link; mirror the hero layout so they look paired

**Iron rule:** never invent a skill, status, file path, or statistic that isn't backed by one of the above.

## Required structure (sim-skills layout)

```
1.  Centered hero block (paired with sim-cli/README.md)
    - <div align="center"> ... </div>
    - Banner image from assets/
    - Tagline mirroring sim-cli's voice
    - Two-line subtitle explicitly cross-referencing sim-cli
    - Shield wall (for-the-badge + flat rows)
    - Section nav: [Skills] · [Protocol] · [Runtime] · [sim-cli]
2.  Banner / teaser — full-width, centered
3.  Why sim-skills? (short — the problem "LLMs have general API knowledge but no operational discipline")
4.  "The skills at a glance" — grid OR table, one row per skill
    - Skill name · domain · execution model · status · sample task
5.  How an agent uses a skill — numbered flow, short
6.  Cross-skill conventions — pulled from CLAUDE.md (Category A/B/C inputs, acceptance rules)
    Link to CLAUDE.md rather than duplicating
7.  Runtime dependency — short, links to sim-cli
8.  Repo layout — pruned, one line per top-level folder
9.  Related projects — sim-cli (paired sibling)
10. License
```

## Asset generation

If `assets/` is empty, create SVGs as part of the task:

| Asset | Notes |
|---|---|
| `assets/banner.svg` | Wide banner. Show 6 skill "cards" laid out in a grid as the visual motif. Same color palette as sim-cli banner (dark bg, blue/purple gradient wordmark) so the two READMEs feel like a pair. |
| `assets/logo.svg` | (Optional) Small stackable icon with "skills" motif — three stacked documents or layers. |

Do NOT reuse sim-cli's banner verbatim — this repo has its own visual identity even while being paired.

## Style rules

Same as sibling fork:
- Emoji section headers allowed (one per header max, must belong to the topic)
- Tables beat prose for "what / how / status" grids
- No banned marketing words (seamless / robust / cutting-edge / revolutionary / powerful)
- No invented stats, stars, contributor counts
- Centered hero, left-aligned body

## Process

1. Read sources in priority order
2. Audit `assets/`; create banner SVG if missing
3. Draft section by section
4. Self-review against checklist below
5. Write README.md
6. Report what changed + what assets still need to be provided (demo GIF etc.)

## Self-review checklist

- [ ] Centered hero paired visually with sim-cli (same palette, same shield style)
- [ ] Tagline explicitly complements sim-cli's tagline
- [ ] Cross-link to sim-cli appears ABOVE the fold
- [ ] Banner SVG committed under `assets/`
- [ ] Every skill listed exists as a `<name>/SKILL.md` in the repo
- [ ] Every skill's status matches what its SKILL.md actually says
- [ ] Cross-skill conventions section links to CLAUDE.md instead of duplicating
- [ ] No banned marketing words
- [ ] Length ≤ 300 lines

## Anti-patterns

| Don't | Why |
|---|---|
| Duplicate sim-cli's feature list | Readers will land on either README; repetition is noise |
| List every file under `<solver>/` | Belongs in the skill folder itself |
| Claim all skills are "production-ready" | Status matters — be honest about Phase A / v0 |
| Paste CLAUDE.md verbatim | Link it |
| Use the exact same banner as sim-cli | Paired ≠ identical |
