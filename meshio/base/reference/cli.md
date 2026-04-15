# meshio CLI

> Applies to: meshio 5.x

The `meshio` command is installed alongside the Python package. Useful
for ad-hoc conversion without writing a Python script.

## Subcommands

```
meshio <command> [options] ...
```

| Command | Purpose |
|---------|---------|
| `convert` (or `c`) | Convert between formats |
| `info` (or `i`) | Print mesh summary |
| `compress` | Apply gzip to XML-based formats |
| `decompress` | Reverse of compress |
| `ascii` (or `a`) | Binary → ASCII |
| `binary` (or `b`) | ASCII → binary |

## convert

```
meshio convert [--input-format IN] [--output-format OUT] IN_FILE OUT_FILE
```

Examples:
```
meshio convert sphere.msh sphere.vtk
meshio convert input.inp output.vtu
meshio convert case.xdmf case.msh --output-format msh4
```

Auto-detects format from extension; use `--input-format` / `--output-format`
to override.

## info

```
meshio info mesh.vtu
```

Output:
```
<meshio mesh object>
  Number of points: 258
  Number of cells:
    triangle: 380
    tetra: 898
  Cell data: gmsh:physical, gmsh:geometrical
```

Use for quick sanity checks on unknown mesh files.

## compress / decompress

XML formats (`.vtu`, `.xdmf`) can be gzipped inline:

```
meshio compress big.vtu              # produces compressed big.vtu (same filename)
meshio decompress big.vtu            # uncompress in place
```

Typical space savings: 50-80%.

## Typical pipelines

### Gmsh → CalculiX
```
gmsh model.geo -3 -o model.msh -format msh22
meshio convert model.msh model.inp --output-format abaqus
```

### Abaqus → ParaView
```
meshio convert job.inp job.vtu
```

### OpenFOAM → VTK
OpenFOAM uses its own native format, so meshio can't directly read. Use:
```
foamToVTK -case my_case
# then ParaView can read directly, or meshio the VTKs further
```

### Big .vtu compressed for web delivery
```
meshio convert big.msh big.vtu
meshio compress big.vtu
```

## Integration with sim

Agent writes a Python script wrapping the conversion (better than CLI
for parseable output):

```python
import json, meshio
mesh = meshio.read("input.msh")
meshio.write("output.vtk", mesh)
print(json.dumps({
    "ok": True,
    "points": len(mesh.points),
    "cells_by_type": {c.type: len(c.data) for c in mesh.cells},
}))
```

Run with `sim run script.py --solver meshio`.
