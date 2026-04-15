# Meshes

## Built-in structured grids

```python
Grid1D(nx=50, dx=0.02)
Grid2D(nx=40, ny=40, dx=0.025, dy=0.025)
Grid3D(nx=20, ny=20, nz=20, dx=0.05, dy=0.05, dz=0.05)
```

Locators: `mesh.facesLeft`, `facesRight`, `facesTop`, `facesBottom`,
`facesFront`, `facesBack`. Use these to constrain BCs.

## Cylindrical / spherical

```python
CylindricalGrid1D(nr=50, dr=0.02)
CylindricalGrid2D(nr=20, nz=40, dr=0.05, dz=0.025)
```

## Unstructured (Gmsh)

```python
mesh = Gmsh2D('domain.msh')
mesh = Gmsh3D('domain.msh')
```

For complex geometries, build the mesh in Gmsh (use the `gmsh-sim`
skill in this repo) and read it here.

## Variable types

| Class | Lives on | Use for |
|---|---|---|
| `CellVariable` | cell centers | unknowns, source coefficients |
| `FaceVariable` | face centers | velocities for ConvectionTerm, fluxes |

Convert between the two:
```python
phi.faceValue                 # FaceVariable from CellVariable
u.cellValue                   # CellVariable from FaceVariable
```
