# Gmsh GEO Scripting Reference

> Applies to: Gmsh 4.x
> Last verified: 2026-04-14

## Kernel choice

```
SetFactory("OpenCASCADE");    // CAD-style: booleans, fillets, STEP/IGES/BREP
// or
SetFactory("Built-in");        // scripted primitives, explicit topology
```

**Rule of thumb**: OpenCASCADE for any CAD-style model or boolean
operations. Built-in for tutorial-style explicit point/line/surface scripts.

## Geometry primitives (OpenCASCADE)

```
Point(1) = {0, 0, 0, meshSize};        // optional mesh size
Line(1) = {1, 2};                      // connects points
Circle(1) = {x, y, z, r};              // full circle
Rectangle(1) = {x, y, z, dx, dy};
Disk(1) = {x, y, z, rx, ry};
Sphere(1) = {x, y, z, r};
Box(1) = {x, y, z, dx, dy, dz};
Cylinder(1) = {x, y, z, dx, dy, dz, r};
Cone(1) = {x, y, z, dx, dy, dz, r1, r2};
Torus(1) = {x, y, z, r1, r2};
```

## Boolean operations (OpenCASCADE only)

```
BooleanUnion(3) = { Volume{1}; Delete; }{ Volume{2}; Delete; };
BooleanDifference(3) = { Volume{1}; Delete; }{ Volume{2}; Delete; };
BooleanIntersection(3) = { Volume{1}; Delete; }{ Volume{2}; Delete; };
BooleanFragments(3) = { Volume{1}; Delete; }{ Volume{2}; Delete; };
```

After any geometry change: nothing explicit in .geo (the script engine
syncs automatically). In Python API you MUST call `occ.synchronize()`.

## Physical groups (CRITICAL for solver export)

Without physical groups, Gmsh exports NOTHING by default (or all
elements if `Mesh.SaveAll = 1`). Solvers need tags to identify BCs.

```
Physical Point("origin", 100) = {1};
Physical Curve("wall", 200) = {1, 2, 3};
Physical Surface("inlet", 300) = {1};
Physical Volume("fluid", 400) = {1};
```

Syntax: `Physical <dim>("name", tag) = {entity_ids};`

## Mesh size control

### Hierarchy (first hit wins, unless overridden)
1. Explicit size on Point
2. Size field (Background Field)
3. `Mesh.MeshSizeMin` / `MeshSizeMax`
4. `Mesh.MeshSizeFromCurvature` (adaptive)
5. `Mesh.MeshSizeExtendFromBoundary`

### Simple max size
```
Mesh.MeshSizeMax = 0.3;
```

### Distance-from-entity refinement
```
Field[1] = Distance;
Field[1].PointsList = {1, 2};
Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = 0.02;
Field[2].SizeMax = 0.2;
Field[2].DistMin = 0.1;
Field[2].DistMax = 1.0;
Background Field = 2;
```

## Transforms

```
Translate {dx, dy, dz} { Volume{1}; }
Rotate {{ax,ay,az}, {x0,y0,z0}, angle} { Volume{1}; }
Extrude {dx, dy, dz} { Surface{1}; Layers{n}; Recombine; }
```

## Common full example (sphere)

```
SetFactory("OpenCASCADE");
Sphere(1) = {0, 0, 0, 1.0};
Physical Volume("ball") = {1};
Physical Surface("surf") = {1};
Mesh.MeshSizeMax = 0.3;
```

Run: `gmsh sphere.geo -3 -o sphere.msh -format msh22`

## Gotchas

- OpenCASCADE and Built-in kernels are independent — mixing requires
  `ShapeFromFile` or similar bridges
- `Physical Surface` exports surface elements; `Physical Volume` exports
  volume elements. Both are typically needed.
- After booleans, entity tags may renumber — use `getEntitiesInBoundingBox`
  to re-identify
- `-format msh22` yields MSH 2.2 (widely-compatible). Default is MSH 4.1.
- Comments start with `//` or `/* */`
