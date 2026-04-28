# ParaView Headless Rendering

> Applies to: ParaView 5.12+

## Rendering backends

ParaView supports three rendering backends:

| Backend | Requirement | Quality | Use case |
|---------|-------------|---------|----------|
| **OpenGL** | Display (X11 / GPU) | Best | Local workstation with GPU |
| **OSMesa** | None (CPU software) | Good | Headless servers, CI/CD |
| **EGL** | NVIDIA GPU + drivers | Best | Headless GPU servers |

The conda-forge ParaView build includes **OSMesa** by default.
Binary downloads from paraview.org ship separate OSMesa/EGL variants.

## Headless rendering setup

### Option 1: pvpython with OSMesa build (recommended)

```python
# No special setup needed if ParaView was built with OSMesa
from paraview.simple import *

sphere = Sphere()
Show(sphere)
view = GetActiveView()
view.ViewSize = [1920, 1080]
Render()
SaveScreenshot("output.png")
```

### Option 2: pvbatch (always headless)

```bash
pvbatch render_script.py
# or with MPI for parallel rendering:
mpirun -np 4 pvbatch render_script.py
```

### Option 3: Virtual framebuffer (Linux, non-OSMesa build)

```bash
xvfb-run -a pvpython render_script.py
```

## Camera control

```python
view = GetActiveView()

# Preset positions
ResetCamera()  # fit all objects in view

# Manual camera
view.CameraPosition = [5, 5, 5]       # camera location
view.CameraFocalPoint = [0, 0, 0]     # look-at point
view.CameraViewUp = [0, 0, 1]         # up direction
view.CameraParallelProjection = 0     # 0=perspective, 1=orthographic
view.CameraViewAngle = 30             # field of view (degrees)

# Rotate camera around focal point
camera = GetActiveCamera()
camera.Azimuth(45)     # rotate around vertical axis
camera.Elevation(30)   # rotate around horizontal axis
camera.Roll(0)         # roll around view direction
Render()
```

## Color mapping

```python
# Color by a field
rep = GetRepresentation()
ColorBy(rep, ("POINTS", "pressure"))

# Apply color preset
lut = GetColorTransferFunction("pressure")
lut.ApplyPreset("Viridis (matplotlib)", True)

# Available presets (common):
#   "Viridis (matplotlib)"
#   "Plasma (matplotlib)"
#   "Inferno (matplotlib)"
#   "Cool to Warm"
#   "Cool to Warm (Extended)"
#   "Jet"
#   "Rainbow Uniform"
#   "Blue to Red Rainbow"
#   "X Ray"
#   "Grayscale"

# Custom range
lut.RescaleTransferFunction(0.0, 100.0)

# Scalar bar (legend)
bar = GetScalarBar(lut, GetActiveView())
bar.Title = "Pressure [Pa]"
bar.ComponentTitle = ""
bar.Visibility = 1
bar.TitleFontSize = 16
bar.LabelFontSize = 12
```

## Screenshot options

```python
SaveScreenshot("output.png",
    ImageResolution=[1920, 1080],      # pixel dimensions
    TransparentBackground=0,            # 1 for transparent PNG
    FontScaling="Scale fonts proportionally",
)

# Multiple views side by side
layout = GetLayout()
SaveScreenshot("multi_view.png",
    layout,
    ImageResolution=[3840, 1080],
)
```

## Representation types

```python
rep = GetRepresentation()
rep.Representation = "Surface"          # filled surfaces (default)
# Options: "Surface", "Wireframe", "Points", "Surface With Edges",
#          "Volume", "3D Glyphs", "Outline", "Feature Edges"

rep.Opacity = 0.5                       # 0.0 = transparent, 1.0 = opaque
rep.LineWidth = 2.0                     # wireframe line width
rep.PointSize = 5.0                     # point size
rep.EdgeColor = [0, 0, 0]              # black edges
```

## Annotations

```python
view = GetActiveView()

# Axes widget
view.OrientationAxesVisibility = 1

# Text annotation
text = Text(Text="Case: pipe flow, Re=10000")
Show(text)
rep = GetRepresentation()
rep.WindowLocation = "Upper Left Corner"
rep.FontSize = 18

# Time annotation (for transient)
annot = AnnotateTimeFilter(Input=reader)
Show(annot)
```

## Animation export

```python
scene = GetAnimationScene()
scene.PlayMode = "Snap To TimeSteps"

SaveAnimation("animation.avi",
    GetActiveView(),
    ImageResolution=[1920, 1080],
    FrameRate=24,
)

# Or as image sequence
SaveAnimation("frame.png",
    GetActiveView(),
    ImageResolution=[1920, 1080],
    SuffixFormat=".%04d",
)
# Produces frame.0000.png, frame.0001.png, ...
```

## Gotchas

- **`SaveScreenshot` with `magnification`** is deprecated since 5.12.
  Use `ImageResolution=[W, H]` instead.
- **View size matters for text scaling.** Set `view.ViewSize` before
  rendering to control proportions.
- **Volume rendering** requires point data (not cell data). Use
  `CellDatatoPointData` filter first if needed.
- **Transparent background** only works with PNG format.
- **Multi-view layouts** need explicit `GetLayout()` reference in
  `SaveScreenshot`.
