# Known Issues — Gmsh Driver

## pip wheel CLI wrapper uses `#!/usr/bin/env python`

**Discovered**: 2026-04-14
**Status**: Handled by driver
**Description**: The `gmsh` executable shipped by the `pip install gmsh`
wheel is a tiny Python script with shebang `#!/usr/bin/env python`. On
systems where only `python3` is on PATH (no bare `python`), the shebang
breaks. The driver works around this by invoking the wrapper explicitly:
`<python_exe> <gmsh_script> <args...>` instead of relying on the
shebang.

## `Mesh.<option>` is not geometry

**Discovered**: 2026-04-14
**Status**: Lint warning
**Description**: A .geo file with only `Mesh.MeshSizeMax = 0.3;` is
syntactically valid but has no geometry — nothing to mesh. The driver's
lint emits a warning if no geometry command (Point/Sphere/Volume/etc.)
is detected. The regex explicitly excludes `Mesh.*` options.

## Default format is MSH 4.1

**Status**: By design, but some downstream solvers need MSH 2.2
**Description**: Gmsh 4+ defaults to MSH 4.1, which is hierarchical and
harder to parse. Many solvers (CalculiX, OpenFOAM tools) expect MSH 2.2.
The driver passes `-format msh22` when running .geo files to emit the
wider-compatible format.

## Physical groups required for solver handoff

**Status**: User-input driven
**Description**: Without `Physical Volume("name") = {...};` etc., Gmsh
exports an **empty** mesh by default. If you see 0 elements in the .msh,
check that physical groups cover the entities you want exported — or
set `Mesh.SaveAll = 1;` to override.

## synchronize() required in Python API

**Status**: User-input driven (not driver-side)
**Description**: After any `occ.add*()` or boolean operation, call
`gmsh.model.occ.synchronize()` before meshing or querying entities.
Forgetting this causes "empty" model errors or missing entities in
queries.
