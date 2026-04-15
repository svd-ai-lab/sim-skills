# LAMMPS Script Structure

> Applies to: LAMMPS stable_29Aug2024

## Canonical ordering

LAMMPS input files are command-order sensitive. Any deviation produces
"Illegal ... command" errors.

```
# 1. INITIALIZATION (units MUST be first command-level)
units           lj | real | metal | si | electron
dimension       3
boundary        p p p               # periodic / fixed / shrink-wrap
atom_style      atomic | molecular | full | charge | ...

# 2. SYSTEM DEFINITION (choose one path)
# Path A: create from lattice
lattice         fcc 0.8442
region          box block 0 10 0 10 0 10
create_box      1 box
create_atoms    1 box
mass            1 1.0

# OR path B: read from data file
read_data       system.data

# OR path C: read restart
read_restart    restart.*

# 3. FORCE FIELD
pair_style      lj/cut 2.5
pair_coeff      1 1 1.0 1.0 2.5
# (bond_style, angle_style, etc. for molecules)

# 4. NEIGHBOR LIST
neighbor        0.3 bin
neigh_modify    every 20 delay 0 check no

# 5. INITIAL STATE
velocity        all create 1.5 12345 mom yes rot yes
# minimize 1.0e-4 1.0e-6 100 1000    # (optional pre-relaxation)

# 6. FIXES (time integration + constraints)
fix             1 all nvt temp 1.5 1.5 0.1

# 7. OUTPUT
thermo          100
thermo_style    custom step temp press pe etotal
dump            1 all atom 100 dump.xyz
restart         1000 restart.*

# 8. RUN
run             10000
```

## Rules of thumb

- **units** first, always. It changes what numeric values mean.
- Don't mix `create_atoms` and `read_data` in the same script (box
  already defined).
- Minimize BEFORE aggressive dynamics unless structure is pre-relaxed.
- One `fix` per `atom group` per time-integration type (don't stack
  `fix nve` and `fix nvt` on the same group).

## Common commands by stage

### Init
| Command | Purpose |
|---------|---------|
| `units` | lj / real / metal / si / electron |
| `atom_style` | atomic / molecular / full / charge |
| `dimension` | 2 or 3 |
| `boundary` | x y z, each p / f / s |

### System
| Command | Purpose |
|---------|---------|
| `lattice` | FCC / BCC / HCP / SC + scale |
| `region` | Named region for create_atoms |
| `create_box` | Allocate simulation box |
| `create_atoms` | Place atoms in region |
| `read_data` | Read from external .data file |
| `replicate` | Tile system for larger box |

### Force field
| Command | Purpose |
|---------|---------|
| `pair_style` | lj/cut, eam, tersoff, reaxff, etc. |
| `pair_coeff` | Per-pair-type coefficients |
| `bond_style` | harmonic, morse, fene (polymer) |
| `angle_style` | harmonic, cosine |

### Fix
| Command | Purpose |
|---------|---------|
| `fix N group_id nve` | Constant energy (microcanonical) |
| `fix N group_id nvt temp Tstart Tstop damp` | Nose-Hoover NVT |
| `fix N group_id npt temp ... iso Pstart Pstop damp` | NPT |
| `fix N group_id langevin ...` | Langevin thermostat |

### Run
| Command | Purpose |
|---------|---------|
| `run N` | Advance N steps |
| `minimize etol ftol maxiter maxeval` | Energy minimization |
| `rerun dump.* every N` | Re-analyze existing trajectory |

## Gotchas

- Comments use `#`
- Continuation uses `&` at end of line
- Variables: `variable myvar equal 1.5` then `$myvar` or `${myvar}`
- `group all` is implicit but must be referenced by name in fixes
