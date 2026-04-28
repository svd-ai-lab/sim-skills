# ParaView 5.4 SDK Notes

## Provenance

- Source: Debian 10 package (`apt install paraview`)
- Version: 5.4.1+dfsg4
- Python: 2.7 (bundled with pvpython/pvbatch)
- E2E verified: 2026-04-16

## Key differences from 5.12+

| Feature | 5.4.1 | 5.12+ |
|---------|-------|-------|
| Python runtime | **2.7** | 3.9+ |
| `ImageResolution` in `SaveScreenshot` | Not supported | Supported |
| `magnification` in `SaveScreenshot` | Supported | Deprecated |
| `Threshold.ThresholdRange` | `ThresholdRange = [lo, hi]` | `LowerThreshold`/`UpperThreshold` |
| `CellType` enum | Not available | `pv.CellType.TETRA` etc. |
| Python venv support | No | 5.13+ |
| OSMesa in Debian package | **No** | Depends on build |

## API quirks for 5.4

- **Python 2 string encoding**: Scripts must use `# -*- coding: utf-8 -*-`
  header and avoid unicode in string literals (no `—`, use `--`).
- **`SaveScreenshot` signature**: Use `SaveScreenshot(filename, view, magnification=2)`
  instead of `ImageResolution=[W, H]`.
- **`Threshold` API**: Uses `ThresholdRange = [lo, hi]` instead of separate
  `LowerThreshold`/`UpperThreshold` properties.
- **No `Fetch` in `paraview.servermanager`** for some builds. Use
  `servermanager.Fetch(source)` with try/except.

## Capabilities verified (E2E 2026-04-16)

| Feature | Status |
|---------|--------|
| `Sphere()` | Verified |
| `Wavelet()` | Verified |
| `Contour` | Verified |
| `Slice` | Verified |
| `Threshold` | Verified |
| `Calculator` | Verified |
| `IntegrateVariables` | Verified |
| `SaveScreenshot` | Failed (no OSMesa in Debian build) |
| `SaveData` (CSV) | Not tested (no display for pipeline) |

## Version detection

```bash
pvpython --version
# Output: "paraview version 5.4.1"
pvbatch --version
# Output: "paraview version 5.4.1"
```
