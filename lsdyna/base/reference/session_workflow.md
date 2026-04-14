# LS-DYNA Session Workflow

## What "session" means for LS-DYNA

LS-DYNA itself has **no live process** to talk to (unlike Fluent/Mechanical
which expose gRPC consoles). The session in this skill is a **persistent
Python namespace** that survives across `sim exec` calls, holding:

| Variable | What | Persists across `sim exec`? |
|----------|------|------------------------------|
| `deck` | PyDyna `Deck` being constructed | Yes |
| `kwd` | `ansys.dyna.core.keywords` module | Yes |
| `Deck` | The `Deck` class (for rebuilds) | Yes |
| `workdir` | `Path` to working directory | Yes |
| `run_dyna` | `ansys.dyna.core.run.run_dyna` function | Yes |
| `model` | DPF `Model` (auto-loaded after solve) | Yes |
| `dpf` | `ansys.dpf.core` module | Yes |
| `_data_sources` | DPF `DataSources` (auto-set on solve) | Yes |
| `_result` | User-assignable return value | Reset each call |

**The solver itself is still one-shot inside the session.** Each
`run_dyna(...)` call spawns `lsdyna_sp.exe i=...` as a subprocess and
waits for it to finish. The "session" gives the agent step-by-step
control over *deck construction* and *DPF post-processing* — not over
the solve itself.

## When to use session mode vs one-shot

| Scenario | Mode | Why |
|----------|------|-----|
| User hands you a finished `.k` file, just run it | **One-shot** (`sim run`) | No need for a Python loop; one call does it |
| Building a new model from scratch, agent drafts keywords incrementally | **Session** | Each keyword visible via `sim inspect deck.summary` |
| Parametric sweep (loop over thicknesses/velocities) | **Session** | Reuse `deck` template, vary one keyword, re-solve |
| Post-processing exploration (try different DPF operators) | **Session** | `model` stays loaded, no per-query restart cost |
| Quick smoke test in CI | **One-shot** | Zero Python deps if `.k` is pre-made |

## Lifecycle

```
sim connect --solver ls_dyna [--workdir <dir>]
  → driver.launch()
    → Imports ansys.dyna.core (lazy)
    → Creates empty Deck()
    → Detects ANSYS install, sets PATH for Intel DLLs
    → Returns session_id

sim exec "deck.append(kwd.MatElastic(mid=1, ro=7.85e-6, e=210.0, pr=0.3))"
sim exec "deck.append(kwd.SectionSolid(secid=1, elform=1))"
sim exec "deck.append(kwd.ControlTermination(endtim=1.0))"
  → driver.run() executes each snippet against the persistent namespace

sim inspect deck.summary
  → {n_keywords: 3, has_termination: true, keyword_types: [...]}

sim exec "deck.export_file(str(workdir / 'input.k'))"
sim exec "run_dyna('input.k', working_directory=str(workdir))"
  → Solver runs (one-shot subprocess)
  → On success, DPF Model auto-loads from d3plot

sim inspect results.summary
  → {n_states: 12, n_nodes: 8, time_end: 1.0}

sim exec "_result = float(model.results.displacement.on_last_time_freq().eval().get_field(0).data.max())"
sim inspect last.result
  → {result: 0.0342, label: ..., elapsed_s: 0.05}

sim disconnect
  → Releases namespace; workdir stays on disk for inspection
```

## Inspect targets

| Name | Returns | When to use |
|------|---------|-------------|
| `session.summary` | session_id, workdir, deck/model loaded flags | Anytime — check what's set up |
| `deck.summary` | n_keywords, title, type counts, completeness flags | After adding keywords — verify what you added |
| `deck.text` | Full serialized .k content | Before solve — preview the .k file |
| `workdir.files` | Files in workdir, d3plot_present flag | After solve — confirm output exists |
| `results.summary` | n_states, n_nodes, n_elements, time range | After solve — verify model is loaded |
| `last.result` | The previous `run()` record (stdout/result/elapsed) | Right after an `exec` — get the return value |

## Patterns

### Pattern 1 — Build deck incrementally with feedback

```bash
sim connect --solver ls_dyna
sim exec "deck.title = 'Cantilever beam tutorial'"
sim exec "deck.append(kwd.ControlTermination(endtim=0.001))"
sim inspect deck.summary
# → Check has_termination is true, n_keywords is 1

sim exec "deck.append(kwd.MatElastic(mid=1, ro=7.85e-6, e=210.0, pr=0.3))"
sim inspect deck.summary
# → has_material is true, n_keywords is 2

# ... continue adding nodes, elements, BCs, loads ...

sim inspect deck.text
# → preview the full .k content before exporting
```

### Pattern 2 — Parametric sweep

```python
# Run once, then loop with sim exec calls:
sim exec "thicknesses = [0.5, 1.0, 1.5, 2.0]"
sim exec """
results = []
for t in thicknesses:
    # Modify thickness keyword
    section = next(k for k in deck if isinstance(k, kwd.SectionShell))
    section.t1 = t
    section.t2 = t
    section.t3 = t
    section.t4 = t
    # Write and solve
    case_dir = workdir / f't_{t}'
    case_dir.mkdir(exist_ok=True)
    deck.export_file(str(case_dir / 'input.k'))
    run_dyna('input.k', working_directory=str(case_dir))
    # Post
    ds = dpf.DataSources()
    ds.set_result_file_path(str(case_dir / 'd3plot'), 'd3plot')
    m = dpf.Model(ds)
    disp = m.results.displacement.on_last_time_freq().eval().get_field(0)
    import numpy as np
    results.append({'t': t, 'max_disp': float(np.linalg.norm(np.asarray(disp.data).reshape(-1,3), axis=1).max())})
_result = results
"""
sim inspect last.result
```

### Pattern 3 — Mixed mode (one-shot solve, then session post-process)

```bash
# Solve via one-shot for run history tracking
sim run input.k --solver ls_dyna

# Then connect to inspect results interactively
sim connect --solver ls_dyna --workdir <run_dir>
sim exec "ds = dpf.DataSources(); ds.set_result_file_path(str(workdir/'d3plot'), 'd3plot'); model = dpf.Model(ds)"
sim inspect results.summary
sim exec "_result = list(model.metadata.time_freq_support.time_frequencies.data_as_list)"
sim inspect last.result
```

## Auto-DPF loading

After any successful `run()` snippet, the runtime checks if a `d3plot`
appeared in `workdir`. If yes (and DPF is available), it auto-instantiates
`model = dpf.Model(d3plot)` so subsequent `sim inspect results.summary`
works without an explicit DPF setup snippet.

This auto-load uses `awp_root` (set at `launch` time) to start the local
DPF server. If the user's environment already has a DPF server running,
the auto-start no-ops.

## Failure modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| `launch()` raises `RuntimeError: PyDyna SDK not installed` | `ansys-dyna-core` missing | `pip install ansys-dyna-core` |
| `run("run_dyna(...)")` returns ok=true but no d3plot | LS-DYNA error termination (KI-001) | Read `workdir/d3hsp` for actual error |
| `query("results.summary")` returns "No DPF model loaded" | DPF unavailable or auto-load failed | Manually run `model = dpf.Model(...)` snippet |
| `query("results.summary")` returns "Unable to locate any Ansys installation" | DPF can't find ANSYS | Pass `awp_root` to launch, or set `AWP_ROOT241` env var (KI-011) |
