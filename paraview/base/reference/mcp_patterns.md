# ParaView MCP Patterns

> Source: https://github.com/llnl/paraview_mcp
> These patterns show common ParaView operations extracted from LLNL's
> MCP server implementation.

## Architecture overview

The MCP tool connects to a running `pvserver` process and exposes
23 discrete operations. Key design decisions:

- **No arbitrary script execution** — only structured operations
- **Visual feedback loop** — `get_screenshot()` lets the agent see results
- **Persistent server** — `pvserver --multi-clients` on port 11111

## Common operation patterns

### Load data and inspect

```python
from paraview.simple import *

reader = OpenDataFile("/path/to/data.vtu")
if reader is None:
    raise RuntimeError("Failed to load file")
UpdatePipeline()

# Get available arrays
info = reader.GetDataInformation()
point_info = info.GetPointDataInformation()
arrays = []
for i in range(point_info.GetNumberOfArrays()):
    arr = point_info.GetArrayInformation(i)
    name = arr.GetName()
    components = arr.GetNumberOfComponents()
    lo, hi = arr.GetComponentRange(0)
    arrays.append({"name": name, "components": components,
                    "range": [lo, hi]})
```

### Create iso-surface

```python
source = GetActiveSource()
contour = Contour(Input=source)
contour.ContourBy = ["POINTS", field_name]
contour.Isosurfaces = [value]
UpdatePipeline()
Show(contour)
ColorBy(GetRepresentation(), ("POINTS", field_name))
Render()
```

### Create slice

```python
source = GetActiveSource()
slice_filter = Slice(Input=source)
slice_filter.SliceType = "Plane"
slice_filter.SliceType.Origin = origin   # [x, y, z]
slice_filter.SliceType.Normal = normal   # [nx, ny, nz]
UpdatePipeline()
Show(slice_filter)
Render()
```

### Compute surface area / volume

```python
source = GetActiveSource()
integrate = IntegrateVariables(Input=source)
UpdatePipeline()

from paraview.servermanager import Fetch
data = Fetch(integrate)
# Result is a single-cell dataset; read from cell data
area = data.GetCellData().GetArray("Area").GetValue(0)
```

### Plot over line (probe)

```python
source = GetActiveSource()
pol = PlotOverLine(Input=source)
pol.Point1 = point1    # [x1, y1, z1]
pol.Point2 = point2    # [x2, y2, z2]
pol.Resolution = 100
UpdatePipeline()

from paraview.servermanager import Fetch
data = Fetch(pol)
n_points = data.GetNumberOfPoints()
field = data.GetPointData().GetArray(field_name)
values = [field.GetValue(i) for i in range(n_points)]
```

### StreamTracer for flow visualization

```python
source = GetActiveSource()
stream = StreamTracer(Input=source, SeedType="Point Cloud")
stream.Vectors = ["POINTS", "Velocity"]
stream.SeedType.Center = seed_center  # [x, y, z]
stream.SeedType.Radius = seed_radius
stream.SeedType.NumberOfPoints = n_seeds
stream.MaximumStreamlineLength = max_length
stream.IntegrationDirection = "BOTH"  # "FORWARD", "BACKWARD", "BOTH"
UpdatePipeline()

tube = Tube(Input=stream)
tube.Radius = tube_radius
Show(tube)
```

### Export to STL

```python
contour = GetActiveSource()  # must be a surface (PolyData)
SaveData("output.stl", contour)
```

### Camera rotation

```python
camera = GetActiveCamera()
camera.Azimuth(azimuth_degrees)
camera.Elevation(elevation_degrees)
Render()
```

## sim snippet pattern

All ParaView snippets for sim should follow this structure:

```python
"""Description of what this snippet does.

Acceptance: <quantitative criterion>
Run: sim run snippet.py --solver paraview
"""
import json
import sys
from paraview.simple import *

def main():
    # 1. Load data or create source
    # 2. Apply filters
    # 3. Compute metrics
    # 4. Optionally render screenshot
    # 5. Print JSON result

    result = {
        "ok": True,
        "step": "description",
        # ... quantitative fields ...
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
```
