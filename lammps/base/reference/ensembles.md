# LAMMPS Ensembles & Thermostats

> Applies to: LAMMPS stable_29Aug2024

## Fix = time integrator / constraint / output hook

The `fix` command is LAMMPS's main knob. Every simulation needs at least
one time-integration fix.

## Ensembles

### NVE (microcanonical - constant energy)
```
fix myfix all nve
```

### NVT (canonical - constant temperature)

Nose-Hoover:
```
fix myfix all nvt temp Tstart Tstop Tdamp
# Tdamp = temperature damping time (usually 100*dt)
```

Langevin (stochastic):
```
fix myfix all nve
fix thermo all langevin Tstart Tstop Tdamp seed
```

### NPT (isobaric-isothermal)
```
fix myfix all npt temp Tstart Tstop Tdamp iso Pstart Pstop Pdamp
# or tri (triclinic), aniso (anisotropic)
```

### NVT with rigid body (colloids/clusters)
```
fix rb all rigid/nvt molecule temp 300 300 100
```

## Typical Tdamp / Pdamp values

| Units | Tdamp | Pdamp |
|-------|-------|-------|
| `lj` | 0.1 | 1.0 |
| `real` | 100 fs | 1000 fs |
| `metal` | 0.1 ps | 1.0 ps |

Rule of thumb: Tdamp ≈ 100 × timestep. Pdamp ≈ 10 × Tdamp.

## Energy minimization (pre-dynamics)

```
minimize  etol ftol maxiter maxeval
# e.g. minimize 1.0e-4 1.0e-6 1000 10000
```

Always minimize before starting aggressive dynamics on a fresh
structure, otherwise NVT/NPT can blow up from atom overlaps.

## Equilibration strategy

1. **Minimize** (remove overlaps)
2. **NVT short** (establish temperature)
3. **NPT short** (establish density/pressure)
4. **Production** (measurement run)

Example:
```
minimize 1e-4 1e-6 1000 10000

velocity all create 300 12345

fix m all nvt temp 300 300 100
run 10000                       # NVT equilibration
unfix m

fix m all npt temp 300 300 100 iso 1.0 1.0 1000
run 10000                       # NPT equilibration
unfix m

fix m all nve
run 100000                      # production
```

## Common mistakes

1. **Two time-integration fixes on same group**:
   ```
   fix 1 all nve
   fix 2 all nvt temp 300 300 100    # WRONG - double integration
   ```

2. **No time-integration fix**:
   ```
   # forgot 'fix X all nve' or similar
   run 1000                          # atoms don't move
   ```

3. **Tdamp too short**:
   ```
   fix m all nvt temp 300 300 0.001  # too tight coupling → oscillation
   ```

4. **Thermostat on entire system when you want a subset**:
   ```
   group frozen type 2
   fix f frozen setforce 0 0 0        # freeze
   fix m mobile nvt temp 300 300 100  # thermostat only mobile
   ```

## Constraint fixes

| fix | Purpose |
|-----|---------|
| `setforce` | Zero forces on group |
| `addforce` | Add constant force |
| `wall/reflect` | Reflecting boundary |
| `wall/lj93` | LJ 9-3 wall |
| `shake` | Rigid bonds (SHAKE/RATTLE) |
| `rigid` | Rigid body integrator |
| `spring` | Harmonic restraint |
