# Workflow — MAPDL 2D I-beam (Tier A vendor verification)

**Source**: https://mapdl.docs.pyansys.com/version/stable/examples/gallery_examples/00-mapdl-examples/mapdl_beam.html

**Physics**: static structural, BEAM188 I-section, simply supported at
both ends, 22.84 kN point load at mid-span.

## Run

```bash
sim run scripts/run.py --solver mapdl
```

## Acceptance gates

1. `exit_code == 0`
2. `ok=True` in JSON output
3. Deflection sign = downward (negative UZ)
4. Deflection magnitude in [0, 1] cm

## Evidence

- `evidence/physics_summary.json` — numerical summary of the run
- `evidence/mapdl_beam_disp_z.png` — UZ colormap over the deformed beam

## Result snapshot (2026-04-14, run #95)

| Quantity | Value |
|---|---|
| Nodes / elements | 23 / 22 |
| Runtime | 9.3 s |
| Max abs deflection | 0.0265 cm |
| Physics | ✓ Matches PL³/(48EI) estimate |
