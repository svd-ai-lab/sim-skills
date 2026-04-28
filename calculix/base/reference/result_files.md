# CalculiX Result Files

> Applies to: CalculiX 2.11–2.20

## File zoo

| File | Format | Written by | Contents |
|------|--------|-----------|----------|
| `<job>.frd` | ASCII / binary | `*NODE FILE`, `*EL FILE` | Field results (visualizable in cgx/ParaView) |
| `<job>.dat` | ASCII tables | `*NODE PRINT`, `*EL PRINT` | Easy-to-parse numeric tables |
| `<job>.sta` | ASCII | Always | Convergence / increment info |
| `<job>.cvg` | ASCII | Always | Per-iteration convergence history |
| `<job>.msg` | ASCII | When warnings/errors | Solver messages |
| `spooles.out` | ASCII | SPOOLES solver | Linear-solver diagnostics |

## Parsing `.dat` for numeric results

`*NODE PRINT` writes tables like:

```
 displacements (vx,vy,vz) for set NALL and time  0.1000000E+01

         1  6.617445E-24  4.160626E-18  0.000000E+00
         2 -6.713884E-07 -6.261028E+02  1.136910E-05
         3 -1.342789E-06 -2.002205E+03  3.770545E-05
```

Regex for extracting node + displacement:
```python
re.compile(r"^\s*(\d+)\s+([-\dE.+]+)\s+([-\dE.+]+)\s+([-\dE.+]+)", re.MULTILINE)
```

Multiple blocks possible (one per step/set). Find the block after the
header `displacements (vx,vy,vz) for set <NAME> and time <T>`.

## Parsing `.frd` (if `.dat` unavailable)

`.frd` is the main binary-ish results format. Key block markers:

```
    1C                        # begin model/coords
    2C                        # begin topology
 -4  <FIELD_NAME>        N C
 -5  <COMPONENT_NAME>    1 n c s e
 -1  <node_id>     <value_1> <value_2> ...
 -3                        # end field block
```

For "DISP" (displacement) field:
```
 -4  DISP        4    1
 -5  D1          1    2    1    0
 -5  D2          1    2    2    0
 -5  D3          1    2    3    0
 -5  ALL         1    2    0    0    1ALL
 -1         1  0.00000E+00  0.00000E+00  0.00000E+00  ...
```

Prefer `.dat` for programmatic extraction — `.frd` parsing is brittle.

## Common field keys

| Key | Field | Per-component names |
|-----|-------|---------------------|
| U | Displacement | U1, U2, U3 |
| S | Cauchy stress | S11, S22, S33, S12, S13, S23 |
| E | Total strain | E11, ... |
| NT | Nodal temperature | NT |
| HFL | Heat flux | HFL1, HFL2, HFL3 |
| RF | Reaction force | RF1, RF2, RF3 |

## Postprocessing

- `cgx <job>.frd` — native CalculiX viewer
- ParaView can open `.frd` via `CalculiX Reader` plugin
- Convert to `.vtk` via external scripts (ccx2paraview)
