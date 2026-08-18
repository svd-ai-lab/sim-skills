---
name: sim-paper-reproduction
description: Cross-solver discipline for extracting simulation evidence from papers, reproducing reference results, and turning verified solver evidence into manuscript or report claims. Use with the relevant solver skill; this skill covers task framing, provenance, staged acceptance, and publication handoff rather than solver-specific commands.
---

# sim-paper-reproduction

Use this skill when the user wants to reproduce, validate, or diagnose a
simulation from a paper, report, thesis, benchmark, or reference study.

This is a **task skill**, not a solver driver. Pair it with the relevant solver
skill, such as HFSS, COMSOL, Fluent, MATLAB, or a plain Python library. The
execution tool is not fixed: use `sim-cli` when it adds discovery, session
control, inspection, logs, or artifact tracking; use solver-native scripts,
plain Python, vendor batch executables, or GUI workflows when they are the
right primitive.

## Paper Evidence Map

Before turning a paper into model inputs, build a compact evidence map for the
parts that affect the task. For each fact, record the page or section, source
object (text, equation, table, figure, caption, or supplement), extracted value
and unit, and status: `direct`, `derived`, `inferred`, `ambiguous`, or `missing`.

- Keep figure axes, legends, series identity, normalization, and coordinate
  conventions with any digitized values.
- Preserve conflicting text/table/figure values as separate evidence until the
  conflict is resolved; do not silently choose one.
- Treat OCR and visual readings as candidates until checked against text,
  captions, equations, or another source.
- Carry only `direct` or explicitly justified `derived` facts into the
  parameter manifest. Keep inferred values visible as assumptions.

## Reproduction Loop

1. Define the acceptance target before building.
   - Capture the paper/result identifier, target figures/tables, units,
     coordinate conventions, and numeric pass/fail metrics.
   - A solver exit code, generated plot, or successful export is not acceptance.
2. Build a parameter manifest.
   - For each value, record `value`, `unit`, `source`, `confidence`, and notes.
   - Mark inferred or exploratory values clearly. Do not mix them with
     paper/user-provided values.
   - If a value is missing, leave it missing or run a labelled sensitivity
     study; do not invent it as fact.
3. Create the smallest credible runnable case.
   - First prove the solver can build, solve, and export the leading metric.
   - Use simplifications only when they are explicitly labelled and tracked.
   - Prefer one bounded step at a time so each failure has a clear cause.
   - When the full reference target is large, coupled, or under-specified, use
     progressive fidelity: add geometry detail, secondary physics, coupling,
     sweeps, optimization, or calibration only after the prior layer has
     exported evidence and passed its acceptance check, unless a bypass reason
     is recorded.
4. Gate later results on earlier evidence.
   - If the leading metric fails, stop and diagnose before producing secondary
     figures.
   - The gate depends on the task. For an antenna it may be S-parameters before
     axial ratio and patterns; for another domain it may be residuals,
     conservation, calibration error, or a benchmark norm.
5. Record each iteration.
   - Keep `hypothesis -> change -> evidence -> conclusion -> next hypothesis`.
   - Preserve logs, exported data, solver messages, screenshots/previews, and a
     run manifest.

## Tool Choice

Use the narrowest reliable execution primitive:

- `sim-cli` persistent sessions when inspection, bounded snippets, or shared
  session state are useful.
- `sim run` when the plugin wrapper adds linting, parsing, profile checks, or
  safer execution.
- Plain Python or solver SDK scripts when they are clearer and still produce
  durable artifacts.
- Vendor executables or batch modes when they are the canonical way to solve or
  export the reference case.
- GUI workflows only when the solver cannot expose the required state
  programmatically, and then capture visual evidence after each GUI action.

Whatever path is chosen, keep the same evidence standard: version/install
probe, inputs, bounded execution, logs/messages, exported artifacts, and metric
evaluation.

## Deliverables

For a first pass, produce:

- Parameter manifest with sources and confidence.
- Reproduction record describing the model, simplifications, and setup.
- Exported leading metric data and computed acceptance numbers.
- Solver artifacts needed to rerun or inspect the case.
- Failure diagnosis and next hypotheses when the result does not match.

Do not claim a reproduction is complete until the stated metrics pass. It is
valid and useful to deliver a failed first pass if it has clear evidence.

## Publication Handoff

When the user wants a paper, report, or manuscript structure from the work,
build a claim ledger before drafting results or conclusions. For each proposed
claim, record its status (`verified`, `derived`, `planned`, or `speculative`),
the run and artifact that support it, and the strongest wording the evidence
allows. Planned runs and attractive hypotheses are not results.

For content-preserving manuscript edits, state the preservation contract before
changing the document: which scientific facts, numeric values, citations,
figure pixels, and wording must remain unchanged, and whether reordering,
headings, captions, cross-references, or formatting may change. Verify the
finished artifact against that contract as well as its rendered layout.

## Boundaries

- This skill does not provide PDF/OCR extraction policy.
- Do not encode a paper's geometry, parameters, figure numbers, or expected
  curves here. Keep those in the case artifact or dataset.
- Solver-specific launch, geometry, meshing, boundary, and export details belong
  in the solver skill or the solver connector.
