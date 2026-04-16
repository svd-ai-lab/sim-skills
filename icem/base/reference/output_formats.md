# ICEM CFD output formats

> Source: ICEM install /icemcfd/output-interfaces/ + help/output/
> Last verified: 2026-04-16

ICEM ships 143 output interface `.tcl` modules under
`<ICEMCFD_ROOT>/win64_amd/icemcfd/output-interfaces/`.

## Most-used exports

| Solver | Interface | Tcl call | Output file |
|---|---|---|---|
| Ansys Fluent | `fluent.tcl` | `ic_save_mesh "out.msh" fluent` | `.msh` (V4/BFC) |
| Ansys CFX | `cfx-5.tcl` | `ic_save_mesh "out.cfx" cfx` | `.cfx` definition |
| Ansys MAPDL | `ansys.tcl` | `ic_save_mesh "out.inp" ansys` | `.inp` APDL batch |
| Abaqus | `abaqus.tcl` | `ic_save_mesh "out.inp" abaqus` | `.inp` |
| LS-DYNA | `lsdyna3d.tcl` | `ic_save_mesh "out.k" lsdyna3d` | `.k` keyword |
| Nastran | `nastran.tcl` | `ic_save_mesh "out.bdf" nastran` | `.bdf` / `.nas` |
| OpenFOAM | (custom) | Export as polyMesh | `constant/polyMesh/` |
| Star-CCM+ | (manual) | via intermediate .msh or .cgns | `.msh` / `.cgns` |
| CGNS | `cgns.tcl` | `ic_save_mesh "out.cgns" cgns` | `.cgns` |
| Tecplot | `tecplot.tcl` | `ic_save_mesh "out.plt" tecplot` | `.plt` |

## How output interfaces work

Each `.tcl` file under `output-interfaces/` defines a `<solver>_write_input`
proc that:
1. Selects the domain (super or sub-domains)
2. Loads boundary condition + topology files
3. Prompts for output path and solver-specific options
4. Writes the mesh data in the target format

In batch mode, these procs are called via Tcl scripting — no GUI prompts.

## Quality of export

ICEM exports are generally high-quality because ICEM stores the mesh
internally in a solver-neutral format (structured blocks or unstructured
domains) and each output interface handles solver-specific numbering,
element ordering, and BC mapping.

**Known issue**: some output interfaces assume GUI availability (dialogs
for file selection). In batch mode, always specify file paths explicitly
in the Tcl script rather than relying on interactive prompts.
