# paraview.simple API Reference

> Applies to: ParaView 5.12+

The `paraview.simple` module is the high-level Python API for ParaView.
Every source, reader, filter, and writer in ParaView has a corresponding
Python function.

## Pipeline model

ParaView uses a **pipeline architecture**: Source → Filter → Filter → Representation → View.

```python
from paraview.simple import *

# 1. Create or load data (source)
reader = OpenDataFile("mesh.vtu")
UpdatePipeline()  # CRITICAL: triggers lazy evaluation

# 2. Apply filters
clip = Clip(Input=reader)
clip.ClipType = "Plane"
clip.ClipType.Normal = [0, 0, 1]
UpdatePipeline()

# 3. Display
Show(clip)
rep = GetRepresentation()
rep.Representation = "Surface"
ColorBy(rep, ("POINTS", "pressure"))

# 4. Render
view = GetActiveView()
ResetCamera()
Render()
SaveScreenshot("output.png")
```

## Readers (auto-detect via OpenDataFile)

```python
reader = OpenDataFile("file.vtu")     # auto-detects format
UpdatePipeline()
```

Explicit readers when auto-detect fails:

| Function | Extensions |
|----------|-----------|
| `LegacyVTKReader(FileNames=[...])` | `.vtk` |
| `XMLUnstructuredGridReader(FileName=[...])` | `.vtu` |
| `XMLPolyDataReader(FileName=[...])` | `.vtp` |
| `XMLImageDataReader(FileName=[...])` | `.vti` |
| `XMLStructuredGridReader(FileName=[...])` | `.vts` |
| `PVDReader(FileName=...)` | `.pvd` (time series) |
| `OpenFOAMReader(FileName=...)` | `.foam` |
| `EnSightReader(CaseFileName=...)` | `.case` |
| `ExodusIIReader(FileName=[...])` | `.e`, `.exo` |
| `CGNSSeriesReader(FileNames=[...])` | `.cgns` |
| `STLReader(FileNames=[...])` | `.stl` |
| `XDMFReader(FileNames=[...])` | `.xdmf` |
| `CSVReader(FileName=...)` | `.csv` |

## Sources (geometric primitives)

```python
sphere   = Sphere(Radius=1.0, ThetaResolution=32, PhiResolution=32)
cone     = Cone(Height=2.0, Radius=0.5, Resolution=32)
cylinder = Cylinder(Radius=0.5, Height=2.0, Resolution=32)
box      = Box(XLength=1, YLength=1, ZLength=1)
plane    = Plane(XResolution=10, YResolution=10)
line     = Line(Point1=[0,0,0], Point2=[1,0,0])
wavelet  = Wavelet()  # 3D scalar test dataset
text     = Text(Text="Hello")
```

## Filters

### Geometric

```python
clip = Clip(Input=source)
clip.ClipType = "Plane"           # or "Box", "Sphere", "Cylinder"
clip.ClipType.Origin = [0, 0, 0]
clip.ClipType.Normal = [1, 0, 0]

slice = Slice(Input=source)
slice.SliceType = "Plane"
slice.SliceType.Origin = [0, 0, 0]
slice.SliceType.Normal = [0, 0, 1]

contour = Contour(Input=source)
contour.ContourBy = ["POINTS", "pressure"]
contour.Isosurfaces = [101325.0, 200000.0]

threshold = Threshold(Input=source)
threshold.Scalars = ["POINTS", "Temperature"]
threshold.LowerThreshold = 300.0
threshold.UpperThreshold = 500.0
```

### Computational

```python
calc = Calculator(Input=source)
calc.Function = "mag(Velocity)"
calc.ResultArrayName = "speed"

grad = GradientOfUnstructuredDataSet(Input=source)
grad.ScalarArray = ["POINTS", "pressure"]

integrate = IntegrateVariables(Input=source)
UpdatePipeline()
# Result is a single-cell dataset with integrated values

plotLine = PlotOverLine(Input=source)
plotLine.Point1 = [0, 0, 0]
plotLine.Point2 = [1, 0, 0]
plotLine.Resolution = 100
```

### Flow visualization

```python
stream = StreamTracer(Input=source, SeedType="Point Cloud")
stream.Vectors = ["POINTS", "Velocity"]
stream.MaximumStreamlineLength = 10.0

tube = Tube(Input=stream)
tube.Radius = 0.01

glyph = Glyph(Input=source, GlyphType="Arrow")
glyph.OrientationArray = ["POINTS", "Velocity"]
glyph.ScaleArray = ["POINTS", "speed"]
glyph.ScaleFactor = 0.1
```

### Data manipulation

```python
cellToPoint = CellDatatoPointData(Input=source)
pointToCell = PointDatatoCellData(Input=source)
clean = Clean(Input=source)        # remove duplicate points
extract = ExtractSurface(Input=source)
```

## Display and rendering

```python
# Show / hide
Show(source)
Hide(source)

# Representation
rep = GetRepresentation()
rep.Representation = "Surface"     # Surface, Wireframe, Points,
                                   # Surface With Edges, Volume

# Color by field
ColorBy(rep, ("POINTS", "pressure"))
# or cell data:
ColorBy(rep, ("CELLS", "Temperature"))

# Color map
lut = GetColorTransferFunction("pressure")
lut.ApplyPreset("Viridis (matplotlib)", True)
# Other presets: "Cool to Warm", "Jet", "Rainbow Uniform",
#   "Blue to Red Rainbow", "Plasma (matplotlib)"

# Scalar bar
bar = GetScalarBar(lut, GetActiveView())
bar.Title = "Pressure [Pa]"
bar.Visibility = 1

# Camera
view = GetActiveView()
view.CameraPosition = [5, 5, 5]
view.CameraFocalPoint = [0, 0, 0]
view.CameraViewUp = [0, 0, 1]
ResetCamera()

# Render and save
Render()
SaveScreenshot("output.png",
    ImageResolution=[1920, 1080],
    TransparentBackground=0)
```

## Data access (querying values)

```python
from paraview.simple import *
from paraview.servermanager import Fetch

reader = OpenDataFile("result.vtu")
UpdatePipeline()

# Get data info
info = reader.GetDataInformation()
n_points = info.GetNumberOfPoints()
n_cells = info.GetNumberOfCells()
bounds = info.GetBounds()  # (xmin, xmax, ymin, ymax, zmin, zmax)

# List available arrays
point_info = info.GetPointDataInformation()
for i in range(point_info.GetNumberOfArrays()):
    arr = point_info.GetArrayInformation(i)
    print(f"{arr.GetName()}: range {arr.GetComponentRange(0)}")

cell_info = info.GetCellDataInformation()
for i in range(cell_info.GetNumberOfArrays()):
    arr = cell_info.GetArrayInformation(i)
    print(f"{arr.GetName()}: range {arr.GetComponentRange(0)}")

# Fetch actual numpy data (small datasets only)
data = Fetch(reader)
pressure = data.GetPointData().GetArray("pressure")
for i in range(pressure.GetNumberOfTuples()):
    val = pressure.GetValue(i)
```

## Writers

```python
# Auto-detect by extension
SaveData("output.csv", source)
SaveData("output.vtu", source)
SaveData("output.stl", source)

# Animation
SaveAnimation("frames.png", view,
    ImageResolution=[1920, 1080],
    FrameRate=30)
```

## Pipeline management

```python
GetActiveSource()         # currently selected source/filter
SetActiveSource(source)   # select a source/filter
GetSources()              # dict of all pipeline objects
Delete(source)            # remove from pipeline
GetActiveView()           # current render view
GetViews()                # all views
```

## Gotchas

- **Always call `UpdatePipeline()`** after creating readers/filters
  before accessing data. The pipeline is lazy.
- **`OpenDataFile` returns None** if the format is unrecognized.
  Always check the return value.
- **`FileName` vs `FileNames`**: Some readers take a string, others
  take a list. Check the specific reader's signature.
- **`ContourBy` uses `["POINTS", "fieldname"]`** format, not just
  the field name string.
- **`SaveScreenshot` resolution** is set via `ImageResolution=[W, H]`,
  not `magnification` (deprecated in 5.12+).
- **pvpython vs pvbatch**: pvpython is serial; pvbatch supports MPI
  parallel. Both run headless when no display is available.
