# LS-DYNA Keyword File Format

## Overview

LS-DYNA input files use a keyword-based format. Each keyword begins with `*` in column 1,
followed by data cards in fixed-width fields.

## File structure

```
*KEYWORD                    ← Required first line
*TITLE                      ← Optional title
My simulation description
*CONTROL_TERMINATION        ← Control cards
...data...
*MAT_ELASTIC                ← Material definitions
...data...
*SECTION_SOLID              ← Section definitions
...data...
*PART                       ← Part definitions
...data...
*NODE                       ← Node coordinates
...data...
*ELEMENT_SOLID              ← Element connectivity
...data...
*BOUNDARY_SPC_NODE          ← Boundary conditions
...data...
*LOAD_NODE_POINT            ← Loads
...data...
*DEFINE_CURVE               ← Load curves
...data...
*DATABASE_BINARY_D3PLOT     ← Output control
...data...
*END                        ← Required last keyword
```

## Card format

### Standard format (default)
- **8 characters per field**, right-justified
- Integer and float fields occupy the same width
- Example: `       1` (integer 1 in 8-char field)

### Long format
- **20 characters per field**, activated by appending `+` to keyword
- Example: `*NODE,+` uses 20-char fields for coordinates
- More precision for floating-point values

### Free format
- Comma-separated values, activated by `*KEYWORD_ID` variants
- Not universally supported — avoid unless documented for a specific keyword

## Comments
- Lines starting with `$` are comments
- `$` can appear anywhere in data cards as inline comments (after valid data)

## Parameters
- `*PARAMETER` keyword defines named variables
- Referenced with `&name` in data cards
- Useful for parametric studies

```
*PARAMETER
R endtime  1.0e-03
R force    100.0
*CONTROL_TERMINATION
&endtime
```

## Include files
```
*INCLUDE
path/to/included_file.k
```

## Common unit systems

| System | Length | Time | Mass | Force | Stress | Density |
|--------|--------|------|------|-------|--------|---------|
| SI | m | s | kg | N | Pa | kg/m³ |
| mm-ms-kg | mm | ms | kg | kN | GPa | kg/mm³ |
| mm-s-tonne | mm | s | tonne | N | MPa | tonne/mm³ |
| mm-ms-g | mm | ms | g | N | MPa | g/mm³ |

**Critical**: LS-DYNA has no built-in unit system. The user must ensure all values
are consistent. The most common mistake is mixing density units — steel density is:
- 7850 kg/m³ (SI)
- 7.85e-6 kg/mm³ (mm-ms-kg)
- 7.85e-9 tonne/mm³ (mm-s-tonne)
