---
name: simulation-need-discovery
description: "Use when handling simulation requirement docs, 任务书/specs, client/lab/customer asks, vague modeling requests, paid gigs, or before costly full solves, long runs, sweeps, optimization, calibration, and coupled simulations where the decision, physical model, assumptions, validation evidence, or deliverable must be clear before execution."
---

# Simulation Need Discovery

## Purpose

Use this skill before doing simulation work when the request may not yet be the real
spec. The stated ask is evidence, not a command to blindly implement.

Your job is to identify the real decision, the evidence needed to support that
decision, the smallest acceptable deliverable, and the assumptions that must be
visible before modeling starts.

This skill is intentionally lightweight. It should guide judgment without forcing
a fixed folder layout, filename scheme, solver, geometry package, or modeling recipe.

## Operating Rule

Do not jump straight from request to model.

First answer:

1. What decision will the simulation inform?
2. Who will consume the result?
3. What evidence would be convincing enough?
4. What deliverable is actually being bought, reviewed, or reused?
5. What is unknown enough to change the plan?

If the answer is already clear, proceed. If not, ask only the highest-value
missing questions or propose explicit assumptions.

## Solver Launch Gate

Before a costly full solve, long run, sweep, optimization, calibration, or
multi-physics escalation, establish a compact execution contract:

- Goal
- Physical model
- Boundary conditions and actuation
- Baseline or comparison
- Outputs and acceptance evidence
- Smallest useful smoke

If one P0/P1 ambiguity would change the physical model, ask at most one
decisive question. Otherwise proceed with visible assumptions. Run the smallest
case that can test setup, sign/convention, boundary behavior, and expected
output before launching the full job. Start the full execution only after that
smoke produces the expected evidence, or record why the gate is being bypassed
and what extra risk remains.

## When To Use

Use this skill for:

- Client, lab, advisor, customer, or stakeholder simulation requests.
- Requirement documents, specs, task briefs, 任务书, screenshots, emails, and PDFs.
- Paid gigs or semi-formal deliverables where scope control matters.
- Vague asks such as make a COMSOL model, reproduce this paper, optimize this
  geometry, generate publishable figures, or simulate this design.
- Situations where the user asks what should we actually deliver, how to scope
  this, or whether the stated request is overbuilt.

Do not use this skill as a replacement for solver execution. It routes work; it
does not contain COMSOL, Fluent, Mechanical, Abaqus, OpenFOAM, or electronics
solver mechanics.

## Discovery Workflow

### 1. Extract The Real Need

Read the request as a bundle of clues:

- Stated task: what they explicitly asked for.
- Implied decision: what they need to decide or prove.
- Audience: professor, reviewer, client engineer, internal product team, buyer,
  teammate, or agent runtime.
- Stakes: concept check, feasibility screen, design comparison, paper figure,
  engineering report, quote, demo, or production workflow.
- Deadline and tolerance: quick directional result, defensible model, polished
  deliverable, or reproducible workflow.

Prefer a short restatement of the real decision and the minimum useful
deliverable before proposing implementation.

### 2. Define The Deliverable Contract

Before modeling, make the deliverable concrete enough to prevent drift.

Clarify:

- Final artifact type: model file, geometry file, script, mesh, plots, report,
  comparison table, notebook, slides, screenshots, or a combination.
- Required fidelity: conceptual, geometry-correct, solver-ready, calibrated,
  publication-quality, or handoff-ready.
- Reuse expectation: one-off result, editable parametric workflow, batch sweep,
  product feature, or reproducible repo.
- Success criteria: accepted by whom, based on what checks.
- Exclusions: what the work will not prove.

Keep this flexible. Do not impose exact folders or filenames unless the user,
repo, or product workflow already has a convention.

### 3. Separate Inputs, Assumptions, And Unknowns

Make a compact inventory:

- Fixed inputs: dimensions, materials, boundary conditions, loads, operating
  conditions, images, CAD, paper equations, target figures, units.
- Adjustable assumptions: symmetry, idealized contact, linearity, representative
  volume, effective properties, steady state, simplified physics, geometry
  substitutions.
- Unknowns: missing values, ambiguous geometry, unclear validation data,
  unspecified objective, incompatible deliverable expectations.

Avoid treating every missing detail as equally important.

### 4. Rank Missing Inputs

Rank missing information by how much it can change the plan:

- P0: Blocks even a scoped plan. Ask or stop.
- P1: Changes geometry, solver choice, physics, or deliverable credibility. Ask
  if possible; otherwise propose assumptions clearly.
- P2: Affects accuracy but not the next useful artifact. Record and continue.
- P3: Cosmetic or polish detail. Defer.

Ask only the highest-value missing questions, usually no more than three to five
at once. If momentum matters, propose defaults and continue with visible caveats.

### 5. Pick The Cheapest Useful Artifact

Use the cheapest artifact that answers the current uncertainty:

- A restated scope when the objective is fuzzy.
- A sketch, dimension table, or geometry preview when topology is unclear.
- A mesh or contact/gap sanity check when solver import risk is high.
- A reduced analytical estimate when order of magnitude is unknown.
- A single-case smoke run when boundary conditions or coupling are uncertain.
- A comparison matrix when several modeling routes are plausible.
- A draft figure or report outline when the deliverable standard is unclear.

Do not launch a heavy solver just to discover that the geometry, objective, or
deliverable was misunderstood.

### 6. Apply Progressive Fidelity

For non-trivial simulation work, use progressive fidelity as the default
operating loop:

1. Build the minimum credible model that can test the scoped claim.
2. Solve or export a concrete artifact from that model.
3. Run the acceptance check for the current claim.
4. Add the next fidelity layer only after the prior layer has evidence, or after
   recording a clear reason to bypass the gate.

Do not add detailed geometry, secondary physics, coupling, sweeps, optimization,
calibration, or polished automation until the current layer has evidence that it
runs and supports the scoped claim. If a layer must be skipped because the
decision, data, or stakeholder requirement demands it, document the bypass
reason and the extra risk it creates.

Keep each layer solver-neutral in the plan: name the uncertainty it reduces, the
artifact it will export, and the check that allows escalation.

### 7. Route Geometry And Solver Work

Use `geometry-preview` for topology-aware geometry preflight before heavy solver
work when geometry matters:

- contacts, gaps, cavities, swept paths, lattices, pores, layered structures,
  interlacing, channels, membranes, periodic cells, or imported CAD risk.
- STEP/STL/mesh sanity checks before COMSOL, Fluent, Mechanical, Abaqus, or
  another solver.

Escalate to solver-specific skills only when the uncertainty is solver-specific:

- physics formulation, boundary conditions, meshing strategy, convergence,
  solver settings, material models, coupling, postprocessing, or validation
  against solver outputs.

This skill should not duplicate solver recipes.

### 8. Scope The Modeling Path

When the request is too broad, convert it into a layered path:

- Minimum credible model: the smallest model that can answer the real decision.
- Next fidelity layer: the first upgrade that would materially improve evidence.
- Optional polish: aesthetics, automation, report formatting, or extra sweeps.
- Explicit non-goals: claims that remain outside the evidence.

Use pushback when the stated request asks for full fidelity, full optimization,
paper-quality proof, or all-physics coupling without enough inputs, time, or
validation data.

Good pushback names the risk, offers a cheaper artifact, and states both what
that artifact would and would not prove.

### 9. Validate Before Shipping

Before handing over results, check that the artifact supports the agreed claim:

- Units, dimensions, and coordinate conventions are consistent.
- Geometry has been visually or programmatically sanity-checked when relevant.
- Solver outputs have basic magnitude, trend, and boundary-condition checks.
- Figures are labeled and do not imply more precision than the model supports.
- Assumptions and excluded claims are visible.
- The final deliverable matches the audience and reuse expectation.

If validation is weak, say so plainly and frame the result as exploratory,
directional, or a first-pass model.

## Question Pattern

Prefer targeted questions over intake forms.

Examples: ask what decision the result supports, what would make the recipient
accept the answer, whether the deliverable is a model, figure, report, or
workflow, which inputs are fixed, what reference data exists, and whether the
main risk is geometry, physics fidelity, or delivery speed.

If the user is unavailable, continue with explicit assumptions and identify the
assumption most worth revisiting.

## Anti-Overclaim Rules

Do not claim:

- Optimization when only a few cases were compared.
- Validation when there is no reference data, benchmark, or sanity check.
- Physical proof when the model is a geometry preview or reduced estimate.
- Solver readiness when geometry, mesh, units, or boundary conditions are still
  ambiguous.
- Publication quality when figures or methods would not survive review.

It is fine to produce exploratory artifacts. Label them honestly.

## Lightweight Output Template

When useful, summarize the discovered scope in this shape:

- Real decision:
- Audience:
- Minimum useful deliverable:
- Known fixed inputs:
- Highest-risk unknowns:
- Proposed assumptions:
- Cheapest next artifact:
- Escalation path:
- What this will not prove:

Use the template only when it helps. For simple requests, a short paragraph is
better than ceremony.
