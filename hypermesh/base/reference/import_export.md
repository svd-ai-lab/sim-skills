# HyperMesh Import/Export

> Applies to: HyperWorks Desktop 2024+

## Geometry import (CAD)

### Supported formats

| Format | Reader name | Extensions |
|--------|-------------|------------|
| STEP | `step` | `.step`, `.stp` |
| IGES | `iges` | `.iges`, `.igs` |
| CATIA V5 | `catia` | `.CATPart`, `.CATProduct` |
| CATIA V6 | `catiav6` | various |
| NX | `nx_native` | `.prt` |
| SolidWorks | `solidworks` | `.sldprt`, `.sldasm` |
| Creo/Pro-E | `creo` | `.prt`, `.asm` |
| JT | `jt` | `.jt` |
| Parasolid | `parasolid` | `.x_t`, `.x_b` |
| ACIS | `acis` | `.sat` |
| Rhino | `rhino` | `.3dm` |

### Import pattern

```python
import hm

model = hm.Model()

# Set CAD reader options before import
hm.setoption_cadreader("step", "TargetUnits", "MMKS (mm kg N s)")
hm.setoption_cadreader("step", "CleanupTol", "0.1")

# Import geometry
model.geomimport(filename="part.step")
```

### CAD reader options

```python
# SolidWorks
hm.setoption_cadreader("solidworks", "TargetUnits", "MMKS (mm kg N s)")
hm.setoption_cadreader("solidworks", "CreationType", "Parts")

# IGES
hm.setoption_cadreader("iges", "CleanupTol", "0.1")

# CATIA V6
hm.setoption_cadreader("catiav6", "SplitComponents", "ByBody")
```

## FE model import

```python
# Import FE model file
model.feinputwithdata2(
    filename="model.bdf",
    include_path="",
    translator="OptiStruct",
    # ... additional options
)

# Multi-file batch import
model.feinputwithdata2("file1.bdf", ...)
model.feinputwithdata2("file2.bdf", ...)
model.end_batch_import()

# Preserve include file structure
model.feinputpreserveincludefiles()
model.feinputwithdata2("model.bdf", ...)
```

## HyperMesh model file (.hm)

```python
# Read
model.readfile(filename="model.hm", load_cad_geometry_as_graphics=0)

# Write (save)
model.writefile(filename="output.hm")
```

## FE model export (solver deck)

### Standard export

```python
# Export via template
model.feoutputwithdata(
    template="optistruct",    # or "nastran", "abaqus", "lsdyna", "radioss"
    filename="output.fem",
)
```

### Supported solver formats

| Template | Extension | Solver |
|----------|-----------|--------|
| `optistruct` | `.fem` | Altair OptiStruct |
| `nastran` | `.bdf` | MSC Nastran |
| `abaqus` | `.inp` | Abaqus |
| `lsdyna` | `.k` | LS-DYNA |
| `radioss` | `.rad` | Altair Radioss |
| `pamcrash` | `.pc` | PAM-CRASH |
| `permas` | `.dat` | PERMAS |
| `ansys` | `.cdb` | ANSYS MAPDL |

### Export options

```python
# Export selected entities only
model.feoutput_select(
    template="optistruct",
    filename="partial.fem",
    collection=selected_elements,
)

# Export single include file
model.feoutput_singleinclude(
    template="optistruct",
    filename="include.fem",
    include_id=1,
)

# Export only modified includes
model.feoutputincludes(
    template="optistruct",
    filename="modified.fem",
)
```

## Geometry export (CAD)

```python
# Set export options
hm.setoption_cadwriter("step", "TargetUnits", "MMKS (mm kg N s)")

# Export geometry
model.geomexport(
    filename="output.step",
    format="step",
)

# Supported export formats: iges, step, parasolid, jt, inspire
```

## Batch export for Radioss

```python
# Export Radioss Engine + Starter files
model.hm_batchexportenginefile(...)
```
