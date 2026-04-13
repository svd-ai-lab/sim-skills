# CFX Boundary Condition Types

## INLET

```
BOUNDARY: <name>
  Boundary Type = INLET
  Location = <face>
  BOUNDARY CONDITIONS:
    FLOW REGIME:
      Option = Subsonic
    END
    MASS AND MOMENTUM:
      Option = Normal Speed              # Fixed velocity normal to face
      Normal Speed = 2 [m s^-1]
      # OR
      Option = Mass Flow Rate            # Fixed mass flow
      Mass Flow Rate = 1.379 [kg s^-1]
      # OR
      Option = Cartesian Velocity Components  # U, V, W components
      U = 10 [m s^-1]
      V = 0 [m s^-1]
      W = 0 [m s^-1]
    END
    TURBULENCE:
      Option = Medium Intensity and Eddy Viscosity Ratio
      # OR
      Option = Intensity and Length Scale
      Fractional Intensity = 0.05
      Eddy Length Scale = 4.6 [mm]
    END
  END
END
```

## OUTLET

```
BOUNDARY: <name>
  Boundary Type = OUTLET
  Location = <face>
  BOUNDARY CONDITIONS:
    FLOW REGIME:
      Option = Subsonic
    END
    MASS AND MOMENTUM:
      Option = Average Static Pressure
      Relative Pressure = 0 [Pa]
    END
  END
END
```

## WALL

```
BOUNDARY: <name>
  Boundary Type = WALL
  Location = <face>
  BOUNDARY CONDITIONS:
    MASS AND MOMENTUM:
      Option = No Slip Wall              # Standard stationary wall
      # OR
      Option = Free Slip Wall            # Inviscid wall
    END
    WALL ROUGHNESS:
      Option = Smooth Wall
    END
    HEAT TRANSFER:
      Option = Adiabatic                 # No heat flux
      # OR
      Option = Fixed Temperature
      Fixed Temperature = 350 [K]
    END
  END
END
```

### Rotating Wall
```
BOUNDARY CONDITIONS:
  WALL VELOCITY:
    Option = Rotating Wall
    Angular Velocity = 1 [radian s^-1]
    Axis Definition = Coordinate Axis
    Rotation Axis = Coord 0.3
  END
END
```

### Moving Wall
```
BOUNDARY CONDITIONS:
  WALL VELOCITY:
    Option = Counter Rotating Wall
    # OR
    Option = Specified Velocity
    Wall Velocity U = 3 [m s^-1]
  END
END
```

## OPENING

Used when flow direction is unknown (may enter or leave the domain):

```
BOUNDARY: <name>
  Boundary Type = OPENING
  Location = <face>
  BOUNDARY CONDITIONS:
    FLOW REGIME:
      Option = Subsonic
    END
    MASS AND MOMENTUM:
      Option = Opening Pressure and Direction
      Relative Pressure = 0 [Pa]
    END
  END
END
```

## SYMMETRY

No parameters needed:

```
BOUNDARY: <name>
  Boundary Type = SYMMETRY
  Location = <face>
END
```

## INTERFACE

For periodic boundaries or domain connections:

```
DOMAIN INTERFACE: <name>
  Boundary List1 = <side1>
  Boundary List2 = <side2>
  Interface Type = Fluid Fluid
  INTERFACE MODELS:
    Option = Rotational Periodicity     # Wedge/sector models
    # OR
    Option = Translational Periodicity  # Infinite arrays
    # OR
    Option = General Connection         # GGI (non-matching mesh)
  END
END
```

## Boundary condition patterns from verification cases

| Case | BC Type | Key Settings | Physics |
|------|---------|-------------|---------|
| VMFL015 | Mass flow inlet + Opening outlet | 1.379 kg/s, SST, 25°C isothermal | Pipe flow |
| VMFL017 | Velocity inlet + Pressure outlet | Ma=0.73 compressible, SST, CEL expressions | Transonic airfoil |
| VMFL001 | Rotating walls + Periodicity | Angular velocity 1 rad/s, Laminar | Couette flow |
| VMFL011 | Moving wall + Stationary walls | 2 m/s wall, Laminar, tight convergence | Driven cavity |
