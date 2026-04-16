# ParaView Supported File Formats

> Applies to: ParaView 5.12+

ParaView reads 30+ simulation output formats natively via `OpenDataFile()`.

## VTK native formats

| Extension | Type | Reader |
|-----------|------|--------|
| `.vtk` | Legacy VTK (any type) | `LegacyVTKReader` |
| `.vtu` | XML Unstructured Grid | `XMLUnstructuredGridReader` |
| `.vtp` | XML PolyData | `XMLPolyDataReader` |
| `.vti` | XML Image Data | `XMLImageDataReader` |
| `.vtr` | XML Rectilinear Grid | `XMLRectilinearGridReader` |
| `.vts` | XML Structured Grid | `XMLStructuredGridReader` |
| `.pvtu` | Parallel Unstructured Grid | `XMLPartitionedUnstructuredGridReader` |
| `.pvtp` | Parallel PolyData | `XMLPPolyDataReader` |
| `.pvd` | ParaView Data (time series) | `PVDReader` |
| `.vtkhdf` | VTK HDF5 format | `VTKHDFReader` |

## CFD formats

| Extension | Solver | Reader |
|-----------|--------|--------|
| `.foam` | OpenFOAM | `OpenFOAMReader` |
| `.case` | EnSight | `EnSightReader` |
| `.cgns` | CGNS | `CGNSSeriesReader` |
| `.res` | CFX | Via EnSight export or CGNS |

## FEA formats

| Extension | Solver | Reader |
|-----------|--------|--------|
| `.e`, `.ex2`, `.exo` | Exodus II (Sierra, Abaqus) | `ExodusIIReader` |
| `.xdmf`, `.xmf` | XDMF (FEniCS, Elmer, etc.) | `XDMFReader` |
| `.pvtu` | Parallel VTK (CalculiX via ccx2paraview) | `XMLPartitionedUnstructuredGridReader` |

## Geometry/mesh formats

| Extension | Type | Reader |
|-----------|------|--------|
| `.stl` | STereoLithography | `STLReader` |
| `.obj` | Wavefront OBJ | `OBJReader` |
| `.ply` | Stanford PLY | `PLYReader` |
| `.gltf`, `.glb` | glTF | `glTFReader` |

## Tabular / other

| Extension | Type | Reader |
|-----------|------|--------|
| `.csv` | Comma-separated values | `CSVReader` |
| `.nc` | NetCDF | `NetCDFReader` |
| `.fits` | FITS (astronomy) | `FITSReader` |

## Format selection guide

| Source solver | Best format for ParaView |
|---|---|
| OpenFOAM | `.foam` (native, with time steps) |
| Fluent | `.case` (EnSight export) or `.cgns` |
| CFX | `.cgns` or EnSight `.case` |
| STAR-CCM+ | `.case` (EnSight export) |
| Abaqus | `.odb` → convert to `.vtu` via abaqus2vtk |
| CalculiX | `.frd` → `.vtu` via ccx2paraview |
| Elmer | `.vtu` (native VTK output) |
| MAPDL | `.rst` → `.vtu` via PyMAPDL export |
| LS-DYNA | `.d3plot` → use LS-PrePost or convert |
| COMSOL | `.vtu` export from COMSOL |
| Gmsh | `.msh` → `.vtu` via meshio |
| SU2 | `.vtu` (native Paraview output) |

## Reading time series

```python
from paraview.simple import *

# PVD file (explicit time steps)
reader = PVDReader(FileName="results.pvd")
UpdatePipeline()

# OpenFOAM (automatic time detection)
reader = OpenFOAMReader(FileName="case.foam")
reader.CaseType = "Reconstructed Case"
UpdatePipeline()

# Access time steps
timesteps = reader.TimestepValues
for t in timesteps:
    UpdatePipeline(time=t)
    SaveScreenshot(f"frame_{t:.3f}.png")
```
