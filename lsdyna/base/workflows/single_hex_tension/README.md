# Single Hex Element Tension Test

## Overview

Minimal LS-DYNA verification case: a single 8-node hex element (1×1×1 mm steel cube)
under uniaxial tension. Bottom face fixed, top face loaded in +Z direction.

## Model details

| Parameter | Value |
|-----------|-------|
| Element type | 8-node solid (ELFORM=1) |
| Material | *MAT_ELASTIC (steel, E=210 GPa, ν=0.3) |
| Density | 7.80e-6 kg/mm³ |
| Load | 0.01 kN total (4 × 0.0025 kN per node) = 10 MPa |
| End time | 1.0 ms |
| Analysis type | Explicit dynamics |

## Expected results

| Metric | Value |
|--------|-------|
| Termination | Normal |
| Cycles | ~7129 |
| Timestep | ~1.4e-4 ms |
| Duration | <2 seconds |

## Acceptance criteria

1. `N o r m a l    t e r m i n a t i o n` in output
2. Problem time reaches 1.0
3. Problem cycle > 5000
4. Output files produced: d3plot, d3hsp, glstat, messag

## E2E evidence

See `evidence/e2e_summary.json` for the actual solve results from the driver test run.

## How to run

```bash
sim run single_hex_tension.k --solver ls_dyna
```

Or directly:
```bash
lsdyna_sp.exe i=single_hex_tension.k
```
