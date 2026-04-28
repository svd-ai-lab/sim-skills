# ParaView 5.13 SDK Notes

## Key features

- **Python virtual environment support**: `pvpython --venv /path/to/venv`
  allows adding pip packages to ParaView's Python.
- **Improved VTK HDF reader**: Better performance for large datasets.
- **New CGNS reader improvements**: Faster parallel CGNS loading.
- **EGL rendering improvements**: Better headless GPU rendering.

## API changes from 5.12

- `SaveScreenshot`: `magnification` parameter fully removed.
  Use `ImageResolution=[W, H]`.
- `GetRepresentation()`: New `SelectMapper` property for
  choosing rendering mapper.
- `OpenDataFile`: Improved format auto-detection.

## Version detection

```bash
pvpython --version
# Output: "paraview version 5.13.0"
```

Or within Python:
```python
import paraview
print(paraview.__version__)  # "5.13.0"
```
