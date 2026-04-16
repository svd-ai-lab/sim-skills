# Known Issues — ParaView Driver

## KI-001: ParaView not pip-installable

**Status**: By design
**Description**: Unlike pyvista, ParaView cannot be installed via `pip install`.
Must use conda (`conda install conda-forge::paraview`) or download the
binary from paraview.org.
**Workaround**: Ensure `pvpython` is on PATH, or set `PV_HOME` / `PARAVIEW_HOME`
environment variable to the ParaView install root.

## KI-002: UpdatePipeline() required after every reader/filter

**Status**: API design
**Description**: ParaView's pipeline is lazy. Creating a reader or filter
does NOT immediately execute it. You must call `UpdatePipeline()` before
accessing any data (array names, bounds, etc.). Without it, data
information returns zeros or empty arrays.
**Fix**: Always call `UpdatePipeline()` after creating readers and filters.

## KI-003: Headless rendering requires OSMesa or EGL build

**Status**: Build-time decision
**Description**: `SaveScreenshot()` requires a rendering backend. On headless
servers without a display, ParaView must be built with OSMesa (software
rendering) or EGL (NVIDIA GPU rendering). The standard binary download
from paraview.org may not include OSMesa.
**Workaround**:
- Use conda-forge build (includes OSMesa)
- Download the explicit OSMesa/EGL variant from paraview.org
- Or wrap with `xvfb-run` on Linux

## KI-004: OpenDataFile returns None for unknown formats

**Status**: Expected behavior
**Description**: `OpenDataFile("file.xyz")` returns `None` if ParaView
doesn't recognize the extension. No exception is raised.
**Fix**: Always check `if reader is None` after `OpenDataFile()`.

## KI-005: pvpython vs system Python

**Status**: Architecture constraint
**Description**: `pvpython` is ParaView's bundled Python interpreter. It
has `paraview`, `vtk`, and `numpy` available, but NOT arbitrary pip packages.
If scripts need additional packages (e.g., scipy, pandas), use the conda
install route where you control the Python environment.
**Workaround**: ParaView 5.13+ supports Python venvs (`--venv` flag).

## KI-006: SaveScreenshot magnification deprecated

**Status**: API change in 5.12
**Description**: `SaveScreenshot("out.png", magnification=2)` is deprecated.
Use `ImageResolution=[W, H]` instead.
**Fix**: `SaveScreenshot("out.png", ImageResolution=[1920, 1080])`

## KI-007: ContourBy format

**Status**: API quirk
**Description**: `Contour.ContourBy` requires `["POINTS", "fieldname"]`
format (a two-element list), not just a string field name. Using a bare
string silently fails or raises a cryptic error.
**Fix**: Always use `contour.ContourBy = ["POINTS", "pressure"]`.

## KI-008: FileName vs FileNames parameter

**Status**: API inconsistency
**Description**: Some readers take `FileName="path"` (string), others take
`FileNames=["path"]` (list). `OpenDataFile()` handles this automatically,
but if you use explicit reader constructors, check the docs.
**Fix**: Prefer `OpenDataFile()` for auto-detection. Use explicit readers
only when auto-detection fails.

## KI-009: ParaView 5.4 uses Python 2.7

**Discovered**: 2026-04-16 (E2E on Debian 10)
**Status**: Version-specific
**Description**: ParaView 5.4.1 (Debian package) bundles Python 2.7.
Scripts must include `# -*- coding: utf-8 -*-` header and avoid
unicode characters in string literals (e.g. use `--` not `—`).
**Fix**: Check version first; write Py2-compatible scripts for 5.4.

## KI-010: Threshold API changed between 5.4 and 5.12

**Discovered**: 2026-04-16
**Status**: Version-specific
**Description**: In 5.4, `Threshold` uses `ThresholdRange = [lo, hi]`.
In 5.12+, it uses separate `LowerThreshold` / `UpperThreshold`.
**Fix**: Check ParaView version and use the correct API.

## KI-011: SaveScreenshot signature changed

**Discovered**: 2026-04-16
**Status**: Version-specific
**Description**: 5.4 uses `SaveScreenshot(file, view, magnification=2)`.
5.12+ uses `SaveScreenshot(file, ImageResolution=[W, H])` and
`magnification` is deprecated.
**Fix**: Version-gate the call.
