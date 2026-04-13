# CFD-Post Session File (.cse) Guide

## Running CFD-Post in batch

```bash
# Software rendering (no GPU required)
cfx5post -batch post.cse results_001.res

# GPU rendering (faster, better quality)
cfx5post -batch-gpu-rendering post.cse results_001.res

# Mesa (headless Linux)
cfx5post -batch post.cse -gr mesa results_001.res
```

## Session file structure

### Creating contours

**Important**: Use `Colour Variable`, NOT `Variable`.

```
CONTOUR: PressureContour
  Apply Instancing Transform = On
  Colour Map = Default Colour Map
  Colour Variable = Pressure
  Contour Range = Global
  Domain List = All Domains
  Fringe Fill = On
  Location List = <boundary or plane name>
  Number of Contours = 20
  Surface Drawing = Smooth Shading
  Visibility = On
END
```

### Creating planes

```
PLANE: MidPlane
  Option = XY Plane
  Z = 0.0 [m]
END
```

### Exporting images

```
HARDCOPY:
  Hardcopy Filename = output.png
  Hardcopy Format = png
  Image Height = 1200
  Image Width = 1600
  White Background = On
END
>print
```

**Note**: The `>print` action command must follow the HARDCOPY block.

### Exporting data to CSV

```
EXPORT:
  CSV Separator = ,
  Export File = results.csv
  Export Geometry = Off
  Formatting = Precision 8
  Location List = <plane or boundary>
  Variable List = Pressure, Velocity u, Velocity v, Velocity w
END
>export
```

### Power Syntax in post-processing

Loop over timesteps (transient results):

```
! $List = getValue("DATA READER", "Timestep List");
! @Steps = split(/, /, $List);
! foreach $step (@Steps) {
> load timestep = $step
> HARDCOPY:
>   Hardcopy Filename = frame_$step.png
>   Hardcopy Format = png
>   Image Height = 1200
>   Image Width = 1600
> END
> print
! }
```

## Common gotchas

1. **`Variable` vs `Colour Variable`**: CFD-Post contours use `Colour Variable`, not `Variable`. Using `Variable` causes CCL validation error.
2. **`Path` parameter**: Not valid for PLANE objects — causes "Parameter 'Path' is not allowed" error.
3. **Location must exist**: `Location List` must reference an existing boundary name or user-defined object. Check the .out file for boundary names.
4. **Image not generated**: If `>print` is inside an object block, it won't execute. It must be a standalone action command after the HARDCOPY block ends.
