# LAMMPS Units & Potentials

> Applies to: LAMMPS stable_29Aug2024

## Unit systems

| units | length | time | energy | temp | use for |
|-------|--------|------|--------|------|---------|
| `lj` | sigma | sqrt(m·sigma^2/eps) | epsilon | kT/epsilon | Dimensionless LJ systems |
| `real` | Å | fs | kcal/mol | K | Biomolecules (CHARMM/AMBER) |
| `metal` | Å | ps | eV | K | Metals / solids (EAM, Tersoff) |
| `si` | m | s | J | K | Coarse-grained / continuum |
| `electron` | Bohr | fs | Hartree | K | Electronic ground state |
| `cgs` | cm | s | erg | K | Legacy |

Choosing wrong units is the #1 LAMMPS bug source — copying a timestep
from another unit system gives nonsense.

**Typical timesteps**:
- `lj`: 0.005
- `real`: 0.5–2.0 fs
- `metal`: 0.001–0.005 ps
- `si`: 1e-15 s

## Common pair_styles

| pair_style | Suitable for | Typical pair_coeff |
|------------|-------------|---------------------|
| `lj/cut Rc` | Simple LJ liquids | `1 1 epsilon sigma` |
| `lj/cut/coul/long Rc` | LJ + long-range Coulomb | `1 1 eps sig` + `kspace_style ewald 1e-4` |
| `eam` / `eam/alloy` | Metals (Cu, Al, Fe) | `* * potential.eam.alloy Cu Al` |
| `tersoff` | Covalent (Si, C) | `* * Si.tersoff Si` |
| `reaxff` | Reactive | `* * ffield.reaxff C H O N` |
| `morse Rc` | Diatomic | `1 1 D0 alpha r0` |
| `buck/coul/long Rc` | Buckingham + Coulomb | `1 1 A rho C` |
| `hybrid` | Multi-potential systems | mix styles |

## Example: LJ liquid

```
units           lj
atom_style      atomic

lattice         fcc 0.8442              % number density
region          box block 0 10 0 10 0 10
create_box      1 box
create_atoms    1 box
mass            1 1.0

pair_style      lj/cut 2.5
pair_coeff      1 1 1.0 1.0 2.5        % eps=1, sig=1, cutoff=2.5
```

## Example: EAM Copper

```
units           metal
atom_style      atomic

lattice         fcc 3.615               % Cu lattice const in Å
region          box block 0 10 0 10 0 10
create_box      1 box
create_atoms    1 box
mass            1 63.546

pair_style      eam/alloy
pair_coeff      * * Cu_u3.eam Cu
```

Requires `Cu_u3.eam` file in cwd (download from NIST/OpenKIM).

## Potential file sources

| Site | Content |
|------|---------|
| https://www.ctcms.nist.gov/potentials/ | NIST interatomic potentials DB |
| https://openkim.org/browse/models | OpenKIM models |
| `lammps/potentials/` | Bundled with LAMMPS source |

## Gotchas

- `pair_coeff * * file Cu` with `1` atom type means ALL types use Cu
- LJ `sigma=1.0 epsilon=1.0` is dimensionless — don't confuse with
  `real` units (1 Å, 1 kcal/mol)
- Hybrid pair_style requires one `pair_coeff` line per sub-style
- Missing potential file gives "Unable to open potential file ..."
