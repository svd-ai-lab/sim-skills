# Gmsh Mesh Formats & Solver Handoff

> Applies to: Gmsh 4.x

## MSH format versions

| Version | Default in | Parser difficulty | Common for |
|---------|-----------|-------------------|-----------|
| MSH 2.2 | Pre-Gmsh 4 | Easiest (well documented, simple blocks) | CalculiX, OpenFOAM, legacy tools |
| MSH 4.0 / 4.1 | Gmsh 4+ default | More complex (hierarchical, binary optional) | FEniCS (via dolfinx's gmshio), Gmsh internal |

Force MSH 2.2:
- CLI: `-format msh22`
- .geo: `Mesh.MshFileVersion = 2.2;`
- Python: `gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)`

## MSH 2.2 skeleton

```
$MeshFormat
2.2 0 8
$EndMeshFormat
$PhysicalNames
N
<dim> <tag> "name"
...
$EndPhysicalNames
$Nodes
M
<id> x y z
...
$EndNodes
$Elements
K
<id> <type> <ntags> <tags...> <nodes...>
...
$EndElements
```

Element type codes (MSH 2):
- 1 = 2-node line
- 2 = 3-node triangle
- 3 = 4-node quad
- 4 = 4-node tet
- 5 = 8-node hex
- 6 = 6-node prism
- 11 = 10-node tet (quadratic)
- 15 = 1-node point

## Other export formats

| Format | Flag | Use for |
|--------|------|---------|
| `.vtk` | `-format vtk` | ParaView postprocessing |
| `.cgns` | `-format cgns` | CGNS-compliant solvers |
| `.su2` | `-format su2` | SU2 CFD |
| `.mesh` | `-format mesh` | INRIA format, FreeFEM |
| `.med` | `-format med` | Salome / Code_Aster |
| `.unv` | `-format unv` | I-DEAS universal |
| `.inp` | `-format inp` | **Abaqus / CalculiX input deck** |
| `.stl` | `-format stl` | STL surface mesh |

## Downstream solver handoff

### CalculiX
```
gmsh mesh.geo -3 -format inp -o mesh.inp    # direct INP export
```
Or generate .msh and convert externally with ccx2paraview or custom
scripts.

### OpenFOAM
```
gmsh mesh.geo -3 -format msh22 -o mesh.msh
gmshToFoam mesh.msh                          # OpenFOAM utility
```

### FEniCS / dolfinx
```python
from dolfinx.io import gmshio
mesh, cell_tags, facet_tags = gmshio.read_from_msh("mesh.msh", MPI.COMM_WORLD)
```
Requires MSH 4.x.

### SU2
```
gmsh mesh.geo -3 -format su2 -o mesh.su2
```

## Quality check before handoff

```python
gmsh.model.mesh.optimize("Netgen")
# For hex meshes
gmsh.model.mesh.optimize("Relocate3D")
# High-order
gmsh.model.mesh.optimize("HighOrder")
```

Check minimum element quality:
```python
quality = gmsh.plugin.run("AnalyseMeshQuality")
```
