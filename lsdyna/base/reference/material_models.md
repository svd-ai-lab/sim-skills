# LS-DYNA Material Models

## Most commonly used materials

### *MAT_ELASTIC (MAT_001)
Linear elastic material. Simplest model — good for verification and stiff components.
```
*MAT_ELASTIC
$      MID        RO         E        PR        DA        DB
         1  7.85E-09   210000.       0.3       0.0       0.0
```
- `MID`: Material ID
- `RO`: Density
- `E`: Young's modulus
- `PR`: Poisson's ratio

### *MAT_PLASTIC_KINEMATIC (MAT_003)
Bilinear elastic-plastic with kinematic or isotropic hardening. Good for metals under moderate strains.
```
*MAT_PLASTIC_KINEMATIC
$      MID        RO         E        PR      SIGY      ETAN      BETA
         1  7.85E-09   210000.       0.3     250.0    1000.0       0.0
```
- `SIGY`: Yield stress
- `ETAN`: Tangent modulus (post-yield slope)
- `BETA`: 0=kinematic, 1=isotropic, 0-1=mixed

### *MAT_PIECEWISE_LINEAR_PLASTICITY (MAT_024)
Tabular stress-strain curve. Most flexible metal model.
```
*MAT_PIECEWISE_LINEAR_PLASTICITY
$      MID        RO         E        PR      SIGY      ETAN      FAIL      TDEL
         1  7.85E-09   210000.       0.3     250.0       0.0      0.30       0.0
$       C         P      LCSS      LCSR        VP
       0.0       0.0         1         0       0.0
```
Requires a `*DEFINE_CURVE` (LCSS) for the stress-strain relationship.

### *MAT_RIGID (MAT_020)
Perfectly rigid body — no deformation computed. Used for tooling, fixtures, and ground.
```
*MAT_RIGID
$      MID        RO         E        PR         N    COUPLE         M     ALIAS
         2  7.85E-09   210000.       0.3       0.0       0.0       0.0
$      CMO      CON1      CON2
       1.0         7         7
```
- `CMO=1.0`: Constrain center of mass
- `CON1=7, CON2=7`: Fix all translations and rotations

### *MAT_JOHNSON_COOK (MAT_015)
Rate-dependent plasticity with thermal softening. For high-strain-rate and impact problems.

### *MAT_OGDEN_RUBBER (MAT_077)
Hyperelastic rubber/elastomer material.

## Material selection guide

| Application | Recommended MAT | Notes |
|------------|-----------------|-------|
| Linear verification | MAT_001 (ELASTIC) | Simplest, fastest |
| Metal forming | MAT_024 (PIECEWISE) | With stress-strain curve |
| Crash/impact | MAT_024 + failure | Add FAIL parameter |
| High strain rate | MAT_015 (JOHNSON_COOK) | Rate-dependent |
| Rigid tooling | MAT_020 (RIGID) | No deformation |
| Rubber/polymer | MAT_077 (OGDEN) | Hyperelastic |
