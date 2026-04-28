# Wavelet Filter Pipeline — E2E Evidence

> Verified: 2026-04-16, ParaView 5.4.1, pvbatch, Debian 10 Linux
> Host: remote Linux via SSH (101.6.61.24:2333)

## Pipeline

Wavelet source (3D scalar field) → 5 filters applied and verified.

## Results

### Smoke test (sources only)

```json
{
  "ok": true,
  "step": "smoke-norender",
  "sphere": {
    "n_points": 962,
    "n_cells": 1920,
    "bounds": [-0.999, 0.999, -0.999, 0.999, -1.0, 1.0]
  },
  "wavelet": {
    "n_points": 9261,
    "n_cells": 8000,
    "bounds": [-10.0, 10.0, -10.0, 10.0, -10.0, 10.0],
    "arrays": [{"name": "RTData", "components": 1, "range": [37.35, 276.83]}]
  }
}
```

### Filter tests

```json
{
  "ok": true,
  "step": "filter-tests",
  "contour": {"iso_value": 150.0, "n_points": 3034, "n_cells": 5768},
  "slice": {"n_points": 441, "n_cells": 800},
  "threshold": {"range": [200.0, 300.0], "n_points": 1208, "n_cells": 780},
  "calculator": {"has_DoubleRT": true, "n_arrays": 2},
  "integrate": {"n_cells": 1}
}
```

### Rendering

Failed — ParaView 5.4.1 Debian package not compiled with OSMesa.
No Xvfb available on the server. This is a known limitation (KI-003).
Data pipeline is fully functional; rendering requires either:
- ParaView built with OSMesa (conda-forge build includes it)
- Xvfb installed on the server
- A display (X11 forwarding)

## Scripts used

- `smoke_norender.py` — Sphere + Wavelet sources, data info extraction
- `test_filters.py` — Contour + Slice + Threshold + Calculator + IntegrateVariables
- `test_render.py` — SaveScreenshot attempt (failed on headless 5.4.1)
