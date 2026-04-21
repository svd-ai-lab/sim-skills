# sim-matlab-doc

On-demand search over an installed MATLAB documentation tree. No
browser, no network, no index — just a parallel regex scan over the
per-toolbox HTML folders that MATLAB ships under `<matlabroot>/help/`.

> **For any function / API question, prefer `help('fname')` or
> `doc fname` through the engine (either a live sim session or
> `matlab -batch`).** It's authoritative, toolbox-aware, and works on
> every release. Use this filesystem scanner only as a fallback for
> tutorial / conceptual content, or on older releases where docs
> still ship as HTML. See `matlab/SKILL.md` for the full decision
> rule.

## Known limitation on R2024+

Starting around R2024a, MathWorks stopped shipping static HTML for the
per-toolbox reference pages. The folders `optim/`, `simulink/`,
`stats/`, `signal/`, `control/`, `symbolic/`, … now contain **only
Lucene binary indexes** (`.cfs`/`.cfe`/`.si`) that this scanner cannot
read. The `matlab/` folder still has ~500 HTML files but they're Code
Analyzer diagnostic pages, not function refs. Verified on R2025b:
`search "fft" --module matlab` returns zero hits.

What this scanner still finds on modern installs:
- Simulink learning / tutorial content under `derived/toolbox/learning/`.
- Pockets of HTML under `customdoc/`, `coder/`, and a few other dirs.
- Full core docs on **R2023b and earlier** (static HTML).

For everything else on R2024+, use `matlab -batch "disp(help('<name>'))"`
or `sim exec "disp(help('<name>'))"` in a live session.

## Install

```bash
cd sim-skills/matlab/doc-search
uv sync
```

## Usage

```bash
# Auto-discover MATLAB and print the doc root
uv run sim-matlab-doc where

# Search
uv run sim-matlab-doc search "nonlinear solver" --module optim
uv run sim-matlab-doc search "fft" --module matlab
uv run sim-matlab-doc search "state space" --module control --limit 10

# Scope to Simulink
uv run sim-matlab-doc search "model reference" --module simulink

# Dump full page text for a hit
uv run sim-matlab-doc retrieve matlab/ref/fft.html
```

Searches typically take 1–3 s on a local SSD. Results are ranked by
match count per file.

## How discovery works

`sim-matlab-doc` locates the doc tree in this order:

1. `--matlab-root PATH`
2. `MATLAB_DOC_ROOT` env var (points directly at the `help/` dir)
3. `MATLAB_ROOT` / `MATLABROOT` env var (points at the matlabroot, e.g.
   `/Applications/MATLAB_R2024b.app` or `C:\Program Files\MATLAB\R2024b`)
4. `sim check matlab --json` (reuses sim-cli's install discovery; falls
   back to the legacy `ion` binary)
5. Typical per-OS install paths:
   - macOS:   `/Applications/MATLAB_R*.app`
   - Windows: `C:\Program Files\MATLAB\R*`
   - Linux:   `/usr/local/MATLAB/R*`, `/opt/MATLAB/R*`

When multiple releases are present the newest is preferred (lexical
order on the `Rxxxxy` folder name — `R2024b > R2024a > R2023b`).

The returned path is always the `help/` dir itself, which contains
one subfolder per toolbox (`matlab/`, `simulink/`, `optim/`, `stats/`,
`signal/`, `images/`, `control/`, …). The `--module` filter is a
substring match on that subfolder name, so new toolboxes are picked up
automatically without changes to this package.
