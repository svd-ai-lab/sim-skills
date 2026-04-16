# ParaView 5.13 Solver Notes

ParaView is a post-processor, not a solver. This file documents
version-specific rendering and data handling quirks.

## Rendering

- OSMesa backend works reliably for headless PNG export.
- EGL backend requires NVIDIA driver 535+ on Linux.
- Volume rendering with ray casting: improved performance
  over 5.12 for large structured grids.

## Data handling

- `.foam` reader: improved handling of reconstructed cases
  with large time step counts.
- `.cgns` reader: parallel loading with MPI (pvbatch) now
  supports ADF and HDF5 backends.
- `.pvd` reader: correctly handles relative paths on Windows.

## Known rendering quirk

On Windows with Intel integrated graphics, `SaveScreenshot()` may
produce a black image. Set `view.UseColorPaletteForBackground = 1`
and explicitly set `view.Background = [1, 1, 1]` (white) to work
around this.
