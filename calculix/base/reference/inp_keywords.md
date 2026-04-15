# CalculiX Input Deck Keywords

> Applies to: CalculiX 2.11–2.20
> Last verified: 2026-04-14

## Overview

CalculiX uses **Abaqus-dialect `.inp` files**. Many keywords overlap
exactly; some are CalculiX-only; some Abaqus keywords are unsupported.

## Always-supported keywords

### Model definition
- `*HEADING` — title text
- `*NODE` — node coordinates (`id, x, y, z`)
- `*ELEMENT, TYPE=<type>, ELSET=<name>` — element connectivity
- `*NSET, NSET=<name>` — node set
- `*ELSET, ELSET=<name>` — element set

### Materials
- `*MATERIAL, NAME=<name>` — start material block
- `*ELASTIC` — isotropic elasticity (`E, nu`)
- `*DENSITY` — mass density
- `*CONDUCTIVITY` — thermal conductivity
- `*SPECIFIC HEAT` — specific heat capacity
- `*EXPANSION` — thermal expansion coefficient
- `*PLASTIC` — plasticity (needs hardening data)

### Sections
- `*SOLID SECTION, ELSET=<name>, MATERIAL=<name>` — 2D/3D continuum
- `*SHELL SECTION, ELSET=<name>, MATERIAL=<name>` — shell + thickness
- `*BEAM SECTION, ELSET=<name>, MATERIAL=<name>, SECTION=<shape>` — beam
  - `SECTION=RECT` → rect dims, orientation vector
  - `SECTION=CIRC` → radius

### Boundary / loads
- `*BOUNDARY` — displacement BCs (`node/set, dof_start, dof_end, value`)
- `*CLOAD` — concentrated load (`node/set, dof, magnitude`)
- `*DLOAD` — distributed load
- `*TEMPERATURE` — prescribed temperature (thermal analysis)

### Steps / procedures
- `*STEP [, NLGEOM=YES]` — begin analysis step
- `*STATIC` — static analysis
- `*FREQUENCY, SOLVER=<solver>` — modal analysis
- `*HEAT TRANSFER [, STEADY STATE]` — thermal
- `*COUPLED TEMPERATURE-DISPLACEMENT` — thermomechanical
- `*END STEP` — end step

### Output
- `*NODE PRINT, NSET=<name>` — text output of nodal fields to `.dat`
- `*EL PRINT, ELSET=<name>` — text output of element fields to `.dat`
- `*NODE FILE` — binary/frd output of nodal fields
- `*EL FILE` — binary/frd output of element fields
- `*OUTPUT, FREQUENCY=<n>` — control output frequency

## Common element types

| Type | Description | Nodes | Family |
|------|-------------|-------|--------|
| `C3D8` / `C3D8R` | 3D hex linear | 8 | Continuum |
| `C3D20` / `C3D20R` | 3D hex quadratic | 20 | Continuum |
| `C3D4` | 3D tet linear | 4 | Continuum |
| `C3D10` | 3D tet quadratic | 10 | Continuum |
| `CPS4` / `CPS4R` | 2D plane stress quad | 4 | Continuum |
| `CPE4` / `CPE4R` | 2D plane strain quad | 4 | Continuum |
| `CAX4` | Axisymmetric quad | 4 | Continuum |
| `S3` / `S4` / `S8` | Shell (tri3/quad4/quad8) | 3/4/8 | Shell |
| `B31` / `B32R` | Beam linear/reduced | 2/3 | Beam |
| `T3D2` | 3D truss | 2 | Truss |

## NOT supported (Abaqus keywords that will fail)

- `*STEP, NAME=...` parameter — `NAME` is ignored in CalculiX, use bare `*STEP`
- Some contact-related Abaqus keywords (`*PAIR TRANSFER`, etc.)
- UMAT / user subroutines require compile-time linking
- Most Abaqus `*RESTART` semantics
- `*OUTPUT, HISTORY` — use `*NODE PRINT` instead

If unsure, check the official User's Manual `.pdf` shipped with CalculiX
or the Guido Dhondt homepage.

## Gotchas

- Keywords are case-insensitive (`*STEP` = `*step`) but conventionally UPPER.
- Node/element IDs must be positive integers, gaps allowed.
- `*MATERIAL` must appear before `*SOLID SECTION` references it.
- Beam `SECTION=RECT` requires TWO data lines: (a) dimensions, (b) orientation.
- `*FREQUENCY, SOLVER=SPOOLES` works when spooles is linked (our build).
