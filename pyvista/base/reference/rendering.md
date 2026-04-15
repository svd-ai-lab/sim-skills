# pyvista Rendering (Headless + On-Screen)

> Applies to: pyvista 0.47

## Rendering modes

### Interactive (local display)
```python
import pyvista as pv
grid = pv.Sphere()
plotter = pv.Plotter()
plotter.add_mesh(grid)
plotter.show()                              # blocks until window closed
```

### Off-screen (headless — required in sim pipelines)
```python
import pyvista as pv
pv.OFF_SCREEN = True                        # before creating Plotter

plotter = pv.Plotter(off_screen=True)
plotter.add_mesh(pv.Sphere())
plotter.screenshot("sphere.png", window_size=(1024, 768))
plotter.close()
```

On headless Linux (no X11), additionally:
```python
pv.start_xvfb()                             # spawns virtual X server
```

Or wrap Python invocation in `xvfb-run`:
```
xvfb-run -a python render.py
```

## Plotter basics

```python
plotter = pv.Plotter(
    off_screen=True,
    window_size=(1024, 768),
    background="white",
    multi_samples=4,                        # anti-aliasing
)

# Add meshes with styling
plotter.add_mesh(
    grid,
    scalars="Temperature",                  # color by field
    cmap="viridis",
    show_edges=True,
    edge_color="black",
    opacity=1.0,
)

# Camera
plotter.camera_position = "xz"              # or "yz", "xy", "iso"
plotter.camera.zoom(1.5)
plotter.reset_camera()

# Add annotations
plotter.add_axes()
plotter.add_scalar_bar(title="Temperature [K]")
plotter.add_text("Case: bump flow", position="upper_left")

# Output
plotter.screenshot("output.png")
# or
plotter.export_html("output.html")          # interactive web
plotter.close()
```

## Color maps

Common matplotlib cmap names work:
```
viridis, plasma, inferno, magma   # perceptually uniform (recommended)
jet, rainbow                      # classic (but perceptually bad)
coolwarm, seismic                 # divergent (centered on 0)
Greys, Blues, Reds                # single-hue
```

## Compose multiple viewports

```python
plotter = pv.Plotter(shape=(1, 2), off_screen=True)
plotter.subplot(0, 0)
plotter.add_mesh(grid1, scalars="T")
plotter.subplot(0, 1)
plotter.add_mesh(grid2, scalars="P")
plotter.screenshot("side_by_side.png")
```

## Saving data (not just screenshots)

```python
grid.save("out.vtu")
grid.save("out.vtk")
polydata.save("out.ply")
polydata.save("out.stl")
```

## Time-animation sequence

```python
plotter = pv.Plotter(off_screen=True)
for t, frame in enumerate(frames):
    plotter.clear()
    plotter.add_mesh(frame)
    plotter.screenshot(f"frame_{t:04d}.png")
plotter.close()

# Then: ffmpeg -i "frame_%04d.png" animation.mp4
```

## Gotchas

- Without `OFF_SCREEN = True`, Plotter tries to open a window → fails
  on headless servers
- `start_xvfb()` is idempotent but logs warnings on subsequent calls
- `window_size=(W, H)` affects screenshot resolution, not physics
- Interactive `plotter.show()` blocks — never use in sim scripts
- `add_mesh(scalars="Name")` requires the array to exist on the dataset
  (check `grid.array_names`)
