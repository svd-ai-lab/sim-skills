# meshio Supported Mesh Formats

> Applies to: meshio 5.x

## Format matrix (read/write support)

| Extension | Tool/Origin | Read | Write | Binary option |
|-----------|-------------|------|-------|---------------|
| `.msh` | Gmsh (v2.2 / v4.0 / v4.1) | ✅ | ✅ | yes (MSH 4 binary) |
| `.vtk` | VTK legacy | ✅ | ✅ | yes |
| `.vtu` | VTK XML unstructured | ✅ | ✅ | yes (gz) |
| `.xdmf` / `.xmf` | XDMF (HDF5 backend) | ✅ | ✅ | HDF5 binary |
| `.cgns` | CGNS | ✅ | ✅ | HDF5 binary |
| `.inp` | Abaqus / CalculiX | ✅ | ✅ | text |
| `.mdpa` | Kratos Multiphysics | ✅ | ✅ | text |
| `.obj` | Wavefront OBJ | ✅ | ✅ | text |
| `.ply` | Stanford PLY | ✅ | ✅ | yes |
| `.stl` | Stereolithography | ✅ | ✅ | yes |
| `.msh2` / `.msh4` | Gmsh explicit version | ✅ | ✅ | yes |
| `.h5m` | MOAB | ✅ | ✅ | HDF5 |
| `.med` | Salome MED | ✅ | ✅ | HDF5 |
| `.neu` | GAMBIT neutral | ✅ | ❌ | text |
| `.su2` | SU2 | ✅ | ✅ | text |
| `.f3grid` | FLAC3D | ✅ | ❌ | text |
| `.flac` | FLAC | ✅ | ❌ | text |
| `.wkt` | WKT | ❌ | ✅ | text |
| `.avsucd` | AVS-UCD | ✅ | ✅ | text |
| `.tecplot` | Tecplot ASCII | ✅ | ✅ | text |

## Pick-the-format decision tree

```
Need solver-native format for one of sim's drivers?
  → CalculiX / Abaqus     → .inp
  → Elmer                 → (use ElmerGrid 14 2 to convert .msh)
  → SU2                   → .su2
  → OpenFOAM              → not directly (meshio→VTK→ofMeshToFoam)

Need visualization?
  → ParaView              → .vtu (preferred) or .vtk
  → VisIt                 → .vtk
  → Tecplot               → .tecplot or .vtk

Need lossless archive?
  → .xdmf + HDF5 (best for time series)
  → .msh4 binary

Need cross-tool neutral?
  → .cgns (scientific), .vtu (engineering)
```

## Cell type names in meshio

| meshio | Gmsh code | Abaqus/CalculiX | VTK | Nodes |
|--------|-----------|-----------------|-----|-------|
| `vertex` | 15 | — | 1 | 1 |
| `line` | 1 | — | 3 | 2 |
| `triangle` | 2 | `CPS3` | 5 | 3 |
| `triangle6` | 9 | `CPS6` | 22 | 6 |
| `quad` | 3 | `CPS4` | 9 | 4 |
| `quad8` | 16 | `CPS8R` | 23 | 8 |
| `tetra` | 4 | `C3D4` | 10 | 4 |
| `tetra10` | 11 | `C3D10` | 24 | 10 |
| `hexahedron` | 5 | `C3D8` | 12 | 8 |
| `hexahedron20` | 17 | `C3D20` | 25 | 20 |
| `wedge` | 6 | `C3D6` | 13 | 6 |
| `pyramid` | 7 | `C3D5` | 14 | 5 |

## Physical tag preservation

| From → To | Tags preserved? | Notes |
|-----------|-----------------|-------|
| .msh → .xdmf | ✅ | Via cell_data `gmsh:physical` |
| .msh → .vtk | ⚠️ | Converted to cell scalar |
| .msh → .inp | ✅ | Via `*ELSET` per physical group |
| .vtu → .msh | ⚠️ | Requires manual cell_data → gmsh:physical remap |
| .cgns → .xdmf | ✅ | CGNS "Zone" → XDMF "Grid" |

## Gotchas

- `Mesh.cells` is now a **list of CellBlock**, each with `.type` and
  `.data` — old `dict` API removed in meshio 5.0
- `meshio.read("mesh.msh")` auto-detects format from extension
- Forced format: `meshio.read("mesh.out", file_format="vtk")`
- `file-not-found` errors often stem from `xdmf` referencing a missing
  `.h5` sibling — always keep both files together
