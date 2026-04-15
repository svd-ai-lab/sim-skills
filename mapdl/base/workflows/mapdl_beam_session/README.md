# Workflow — MAPDL 2D I-beam (Phase 2 session mode)

Drives the **same** vendor verification case as `mapdl_beam/` but
through the `sim connect / exec / inspect / disconnect` session
protocol instead of a single `sim run` call. The MAPDL gRPC client
is held alive across 4 incremental exec steps and 3 inspect queries.

**Source**: https://mapdl.docs.pyansys.com/version/stable/examples/gallery_examples/00-mapdl-examples/mapdl_beam.html

## Run

Prereqs: `sim serve --host 127.0.0.1 --port 7600` in another terminal
and `sim connect --solver mapdl` once before launching the harness.

```bash
python scripts/run_session.py
```

## Session transcript (10 steps)

| # | Step | sim command | Latency |
|---|---|---|---|
| 1 | ps-initial | `sim ps` | trivial |
| 2 | inspect-session | `sim inspect session.summary` | trivial |
| 3 | exec-1-prep | `sim exec "mapdl.prep7(); mapdl.et(1,'BEAM188'); ..."` | ~0.03 s |
| 4 | exec-2-mesh | `sim exec "mapdl.n(...); mapdl.e(...); _result=..."` | ~0.06 s |
| 5 | inspect-mesh | `sim inspect mesh.summary` → `{n_nodes:23, n_elements:22}` | trivial |
| 6 | exec-3-solve | `sim exec "mapdl.slashsolu(); mapdl.d(...); mapdl.solve()"` | ~0.08 s |
| 7 | inspect-files-after-solve | `sim inspect workdir.files` → `has_rst=true` | trivial |
| 8 | exec-4-post | `sim exec "mapdl.post1(); uz=... ; plot_*(savefig=...)"` | ~1.28 s |
| 9 | inspect-last-result | `sim inspect last.result` | trivial |
| 10 | disconnect | `sim disconnect` | trivial |

## Acceptance gates

1. All 10 CLI calls succeed (returncode == 0)
2. Mesh inspect returns `n_nodes=23, n_elements=22`
3. After solve, `workdir.files.has_rst == true`
4. Final min UZ in [-0.03, -0.02] cm (physics matches Phase 1 result)
5. Session exits cleanly (`sim disconnect` returns `ok=true`)

## Evidence

- `evidence/transcript.json` — every CLI call's input + stdout/stderr
- `evidence/session_mapdl_beam_uz.png` — headless UZ contour,
  identical physics to Phase 1

## What this proves about Phase 2

- The live `Mapdl` gRPC client survives across 4 separate `sim exec`
  calls (no model-state loss, no re-launch overhead).
- All 4 MAPDL-specific inspect targets (`mesh.summary`,
  `workdir.files`, `last.result`, `session.summary`) flow through the
  server's `/inspect/{name}` fallback into `driver.query()` —
  validates the cross-driver inspect routing (cli.py Choice removal
  + server.py driver.query fallback).
- Headless PNG plotting via PyVista still works inside the live
  session (not only in subprocess one-shot mode).
