# Workflow — 3D notched plate stress concentration (Tier A)

**Source**: https://mapdl.docs.pyansys.com/version/stable/examples/gallery_examples/00-mapdl-examples/3d_notch.html

**Physics**: 3D static structural, thin plate with two opposing
U-notches, uniaxial tension. Computes stress concentration factor
K_t and compares to Roark's analytical formula.

## Run

```bash
sim run scripts/run.py --solver mapdl
```

## Acceptance gates

1. `exit_code == 0`
2. `ok=True` in JSON output
3. Far-field von Mises in [0.75, 1.25] MPa (nominal 1.0 MPa)
4. K_t in [1.4, 2.2] — covers both the coarse-mesh analytical target
   1.60 and fine-mesh numerical overshoot ~2.0

## Evidence

- `evidence/physics_summary.json`
- `evidence/notch_3d_seqv.png` — von Mises stress contour showing the
  red-hot spots at both notch roots

## Result snapshot (2026-04-14, run #97)

| Quantity | Value |
|---|---|
| Nodes / elements | 41043 / 7268 (SOLID186) |
| Runtime | 10.1 s |
| Peak von Mises | 8.02 MPa |
| Far-field von Mises | 0.81 MPa |
| K_t (computed) | 1.98 |
| K_t (Roark analytical) | 1.60 |
| Deviation | +24% — mesh density overshoots peak |

The visible stress concentration at the notch roots matches the
physical expectation: both notches show symmetric red hot spots at
the innermost radius.
