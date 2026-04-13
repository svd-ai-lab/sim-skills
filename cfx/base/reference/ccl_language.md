# CCL (CFX Command Language) Reference

## Syntax rules

- **Case-sensitive**: All keywords and names are case-sensitive
- **Hierarchical**: Objects are nested with `TYPE: Name` ... `END` blocks
- **Comments**: Lines starting with `#`
- **Units**: Values with units use `[brackets]`: `2 [m s^-1]`, `1 [atm]`
- **Line continuation**: Use `\` at line end
- **No underscores in names**: Names may contain alphanumeric characters and spaces only

## Data types

| Type | Syntax | Example |
|------|--------|---------|
| STRING | Plain text | `Material = Water` |
| INTEGER | Whole number | `Maximum Number of Iterations = 200` |
| REAL | With units | `Density = 997 [kg m^-3]` |
| LOGICAL | YES/NO, TRUE/FALSE, ON/OFF | `Global Dynamic Model Control = On` |

## Standard structure

```
LIBRARY:                          ← Material and expression definitions
  CEL:
    EXPRESSIONS:
      <name> = <expression>
    END
  END
  MATERIAL: <name>
    PROPERTIES:
      EQUATION OF STATE:
        Density = <value> [units]
        Option = Value | Ideal Gas
      END
      DYNAMIC VISCOSITY: ...
      SPECIFIC HEAT CAPACITY: ...
      THERMAL CONDUCTIVITY: ...
    END
  END
END

FLOW: <analysis name>             ← Main analysis definition
  SOLUTION UNITS:                 ← Unit system
    Length Units = [m]
    Mass Units = [kg]
    Time Units = [s]
    Temperature Units = [K]
  END
  ANALYSIS TYPE:
    Option = Steady State | Transient
  END
  DOMAIN: <name>                  ← Fluid/solid domain
    Domain Type = Fluid | Solid
    Location = <region name>
    BOUNDARY: <name>              ← Boundary condition
      Boundary Type = INLET | OUTLET | WALL | SYMMETRY | OPENING | INTERFACE
      Location = <face name>
      BOUNDARY CONDITIONS:
        MASS AND MOMENTUM:
          Option = Normal Speed | Mass Flow Rate | ...
          Normal Speed = <value> [m s^-1]
        END
      END
    END
    FLUID MODELS:
      TURBULENCE MODEL:
        Option = Laminar | SST | k epsilon | ...
      END
      HEAT TRANSFER MODEL:
        Option = Isothermal | Total Energy | None
      END
    END
  END
  SOLVER CONTROL:
    CONVERGENCE CONTROL:
      Maximum Number of Iterations = 200
      Timescale Control = Auto Timescale
    END
    CONVERGENCE CRITERIA:
      Residual Target = 1.E-5
      Residual Type = RMS
    END
  END
END

COMMAND FILE:                     ← Version marker (required)
  Version = 24.1
END
```

## CEL expressions

CFX Expression Language allows defining computed quantities:

```
CEL:
  EXPRESSIONS:
    Vinf = 253.483 [m s^-1]
    Drag = force_x()@Wall * cos(2.79[deg]) + force_y()@Wall * sin(2.79[deg])
    Cd = Drag / (0.5 * rho * Vinf^2 * area)
  END
END
```

Expressions can reference:
- Built-in functions: `force_x()`, `area()`, `massFlow()`, `areaAve()`
- Locators: `@BoundaryName`
- Other expressions by name
- Units with `[brackets]`

## Power Syntax (Perl in CCL)

Lines prefixed with `!` are Perl code, `>` are CCL with Perl interpolation:

```
! for my $vel (1.0, 2.0, 3.0) {
>   BOUNDARY: Inlet
>     BOUNDARY CONDITIONS:
>       MASS AND MOMENTUM:
>         Normal Speed = $vel [m s^-1]
>       END
>     END
>   END
! }
```

Built-in functions:
- `getValue("OBJECT", "Parameter")` — read CCL parameter
- `evaluate("Expression")` — evaluate CEL expression, returns `($value, $units)`
