---
name: matlab-sim
description: Use when running MATLAB scripts through the sim runtime — currently one-shot via `sim run --solver matlab`, with persistent local sessions planned for v1. Covers explicit JSON result extraction and conservative handling of MATLAB desktop state.
---

# matlab-sim

Control protocol for executing MATLAB through the `sim` runtime. This skill is for sim-driven execution, not general MATLAB tutoring.

## Phases

| Phase | Status | Description |
|---|---|---|
| **v0** | Current | One-shot `.m` script execution via `sim run --solver matlab` |
| **v1** | Planned | Persistent local MATLAB sessions via `sim connect` / `sim exec` |

## When to use

- Task involves running a `.m` script through sim
- Need machine-readable results extracted via JSON
- Working with MATLAB local install (not remote / not MATLAB Online)

**Do NOT use** for general MATLAB tutoring / API lookup.

## Working rules

1. **Prefer `.m` scripts and explicit JSON outputs** for machine-readable results.
2. **Do not assume MATLAB desktop / session state exists** unless the runtime explicitly exposes it.
3. **When persistent sessions arrive**, treat shared human+agent sessions as cooperative and stateful.
4. **Reuse upstream MATLAB references** when they reduce duplication, but keep `sim` execution assumptions explicit.

## Required protocol — v0 (one-shot)

### Step 0 — Validate inputs
- `.m` script exists at provided path
- Acceptance criterion stated by user (what to extract, what counts as success)
- MATLAB available: `driver.connect().status == "ok"`

### Step 1 — Run
```bash
sim run script.m --solver matlab
```

### Step 2 — Evaluate
- `result.exit_code == 0`
- `result.stderr` empty or warnings only
- `parse_output(result.stdout)` — last `jsonencode(...)` line on stdout — matches the user's acceptance criterion
- **`exit_code == 0` ALONE does NOT satisfy acceptance** — always validate against the criterion

### Step 3 — Report
exit_code, duration, extracted values, stderr if non-empty.

## Script convention

MATLAB scripts driven by sim should print a final `jsonencode(...)` payload when structured output is needed. Errors should remain visible in MATLAB stderr / stdout — do not hide them behind custom wrappers unless the runtime contract requires it.

```matlab
% script.m
result = struct();
result.value = computed_value;
result.ok = true;
disp(jsonencode(result));
```

## File index

### Top-level
- `SKILL.md` — this file
- `LICENSE` — Apache-2.0
- `driver_upgrade.md` — companion sub-skill for evolving the MATLAB driver from v0 → v1 (handles CLI changes, MATLAB Engine API updates, compatibility with upstream MATLAB tooling)

### `reference/` — domain knowledge
- `reference/README.md` — index of MATLAB runtime notes, task templates, and curated upstream links to MathWorks resources

### `workflows/` — end-to-end demos
- `workflows/README.md` — index of MATLAB demo scripts and task workflows

### `snippets/` — reusable snippets (planned)
- `snippets/README.md` — standalone MATLAB snippet files for step-by-step execution (placeholder for v1)

### `tests/` — pytest scaffolding
- `tests/README.md` — integration-test scaffolding for the MATLAB driver

## Upstream references

- [`matlab/matlab-mcp-core-server`](https://github.com/matlab/matlab-mcp-core-server) — official capability baseline
- [`svd-ai-lab/matlab-mcp-server`](https://github.com/svd-ai-lab/matlab-mcp-server) — interactive session / reference design input
- [`matlab/skills`](https://github.com/matlab/skills) — MATLAB agent workflow patterns

## Requirements

- Python 3.10+
- MATLAB installed locally
- `sim-cli` with the MATLAB driver (`MatlabDriver` in `sim.drivers.matlab`)
