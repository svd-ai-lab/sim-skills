# LAMMPS Output: thermo, dump, restart

> Applies to: LAMMPS stable_29Aug2024

## log.lammps

Every run produces `log.lammps` in cwd (override with `log file.log` or
`-log filename` CLI flag).

Contains:
- Echoed input
- Problem setup info (atom count, neighbor list, etc.)
- Thermo output (periodic per `thermo N` command)
- "Loop time ..." footer
- Memory usage, timing breakdown

### thermo block format

```
Step Temp Press PotEng TotEng
   0  1.500 ...  ...   ...
  10  1.472 ...  ...   ...
  50  1.485 ...  ...   ...
Loop time of 0.123 on 1 procs ...
```

Customize columns:
```
thermo_style custom step temp press pe ke etotal density vol
```

Common thermo keywords:
| Keyword | Meaning |
|---------|---------|
| `step` | Timestep count |
| `temp` | Instantaneous kinetic temperature |
| `press` | Pressure |
| `pe` | Potential energy |
| `ke` | Kinetic energy |
| `etotal` | Total energy (pe+ke) |
| `density` | Mass density |
| `vol` | Box volume |
| `lx`/`ly`/`lz` | Box dimensions |
| `pxx`/`pyy`/`pzz` | Stress tensor components |

## dump = trajectory file

```
dump            1 all atom 100 dump.xyz
dump            2 all custom 100 dump.custom id type x y z vx vy vz fx fy fz
dump            3 all dcd 100 traj.dcd
```

Formats:
- `atom` — LAMMPS native text
- `custom` — user-chosen columns (text)
- `xyz` — XYZ text (VMD/OVITO compatible)
- `dcd` — binary DCD (VMD/CHARMM)
- `netcdf` — NetCDF binary
- `yaml` — YAML text

## restart files

```
restart         1000 restart.*          # every 1000 steps, numbered
restart         1000 restart.a restart.b  # toggle pair
write_restart   final.restart           # on-demand
write_data      final.data              # text data file (not binary)
```

## Parsing log.lammps (Python)

```python
import re

text = open("log.lammps").read()
# Find the thermo block: header line + data rows until "Loop time"
m = re.search(
    r"^\s*(Step\s+\w.*)\n([\s\S]*?)^Loop time",
    text, re.MULTILINE,
)
if m:
    header = m.group(1).split()
    rows = [
        line.split() for line in m.group(2).splitlines()
        if line.strip() and line.split()[0].isdigit()
    ]
    last = dict(zip(header, rows[-1]))
    print("Final temp:", last["Temp"])
```

## Acceptance criteria examples

```python
# Temperature equilibration (NVT target 1.5)
assert 0.5 < float(last["Temp"]) < 2.5

# Energy conservation (NVE — drift over N steps)
energies = [float(r[header.index("TotEng")]) for r in rows]
drift = (energies[-1] - energies[0]) / abs(energies[0])
assert abs(drift) < 0.01  # <1% drift

# No NaN / inf
import math
for key in ("Temp", "PotEng", "TotEng"):
    assert math.isfinite(float(last[key])), f"{key} not finite"
```

## Gotchas

- `thermo 0` disables thermo output
- `thermo_modify lost warn` changes "Lost atoms" from fatal to warning
- Dump file sizes grow fast — watch disk space
- `restart` is binary and version-sensitive; use `write_data` for cross-
  version portability
