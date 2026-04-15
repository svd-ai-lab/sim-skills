# Elmer Mesh Workflow

> Applies to: Elmer FEM 9.x–26.x

## Elmer native mesh format

A mesh "directory" contains 4 files:

```
meshname/
├── mesh.header       # counts and element type summary
├── mesh.nodes        # node coordinates
├── mesh.elements     # volume/area element connectivity
└── mesh.boundary     # boundary element connectivity with tags
```

### mesh.header
```
<n_nodes> <n_elements> <n_boundary_elements>
<n_types>
<elem_type_code> <count>
...
```

Element type codes:
- `101` = 1-node point
- `202` = 2-node line
- `303` = 3-node triangle
- `404` = 4-node quad
- `504` = 4-node tetrahedron
- `808` = 8-node hexahedron

### mesh.nodes
```
<node_id> <partition_id> <x> <y> <z>
```
`partition_id = -1` for serial (unpartitioned).

### mesh.elements
```
<elem_id> <body_id> <type_code> <node1> <node2> ... <nodeN>
```

### mesh.boundary
```
<bdry_elem_id> <bdry_id> <parent1> <parent2> <type> <node1> ... <nodeN>
```
`parent2 = 0` for external boundaries.

## Generating meshes

### ElmerGrid from `.grd` (native)

```
ElmerGrid 1 2 input.grd
```
Creates `./<basename>/mesh.*` from a structured grid description.

### ElmerGrid from Gmsh `.msh`

```
ElmerGrid 14 2 mesh.msh -autoclean
```
- Input format 14 = Gmsh
- Output format 2 = Elmer native

### ElmerGrid from other formats

```
# 1  = ElmerGrid native .grd
# 2  = Elmer native (mesh.*)
# 8  = GAMBIT .neu
# 13 = Universal file (.unv)
# 14 = Gmsh .msh
# 17 = MED
# 19 = MED (alternative)
```

Usage: `ElmerGrid <in_fmt> <out_fmt> <file>`

## Minimal `.grd` for unit square

```
Version = 210903
Coordinate System = Cartesian 2D
Subcell Divisions in 2D = 1 1
Subcell Limits 1 = 0 1
Subcell Limits 2 = 0 1
Material Structure in 2D
  1
End
Materials Interval = 1 1
Boundary Definitions
! type  out  int
  1     1    1    1
  2     2    1    1
  3     3    1    1
  4     4    1    1
End
Numbering = Horizontal
Element Degree = 1
Plane Elements = 1000
Triangles = True
Minimum Element Divisions = 10 10
End
```

This creates a 10×10 triangulated unit square with 4 boundaries
(labeled 1,2,3,4 for bottom/right/top/left).

Run: `ElmerGrid 1 2 unit_square.grd` → creates `./unit_square/mesh.*`

## Gmsh → Elmer pipeline

1. Write `.geo` for the geometry
2. `gmsh -2 geom.geo -o geom.msh -format msh22`
3. `ElmerGrid 14 2 geom.msh -autoclean`
4. Edit `.sif` with `Mesh DB "." "geom"`
5. Run `ElmerSolver case.sif`

## Mesh partitioning (for MPI runs)

```
ElmerGrid 2 2 meshname -metis 4          # partition into 4 parts
```
Creates `meshname/partitioning.<N>/` subdirectories.

## Gotchas

- Boundary tag in `.sif` (`Target Boundaries(1) = 3`) must match the
  `<bdry_id>` column in `mesh.boundary`
- `Mesh DB "dir" "name"` resolves to `dir/name/mesh.*` — `dir` is
  relative to `.sif` location
- After ElmerGrid conversion, inspect `mesh.boundary` to verify
  boundary IDs before writing BCs
- 3D meshes need matching element type codes (504 for tet, 808 for hex)
