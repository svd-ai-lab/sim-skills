# Flip-Chip BGA Thermal Characterization

Computes JEDEC-standard thermal resistances (Theta-JB, Theta-JC) for a flip-chip
package on a 2S2P PCB using conduction-only steady-state analysis in Ansys Fluent.

Based on: https://blog.ozeninc.com/resources/flip-chip-thermal-characterization-using-ansys-fluent

## Case file

The case is hosted by Ozen Engineering, not vendored in this repo. Use the
`fetch_case.py` helper — stdlib only, idempotent, runs with plain `python3`
or `uv run`:

```bash
uv run fetch_case.py            # downloads to $SIM_DATASETS/flipchip/
uv run fetch_case.py --force    # re-download even if present
uv run fetch_case.py --dest /some/other/dir
```

If `$SIM_DATASETS` is unset, the script downloads to
`~/.cache/sim-datasets/flipchip/` and tells you to export `SIM_DATASETS` to
match. The demo script then looks for the file at
`$SIM_DATASETS/flipchip/Flip_chip_demo_simplified.cas.h5`.

```powershell
$env:SIM_DATASETS = "C:\path\to\datasets"
```

Manual fallback if the Ozen URL breaks: download the zip from the
[Ozen blog post](https://blog.ozeninc.com/resources/flip-chip-thermal-characterization-using-ansys-fluent)
and place `Flip_chip_demo_simplified.cas.h5` under `$SIM_DATASETS/flipchip/`.

- `Flip_chip_demo_simplified.cas.h5` — Fluent 25.1 format, 455K cells
- 2S2P PCB (4 copper + 3 FR-4 layers), 49 BGA solder balls, die + substrate + underfill
- All materials pre-assigned; energy equation OFF (script enables it)

## What it computes

| Metric | Definition | BC setup |
|--------|-----------|----------|
| Theta-JB | (T_die_max - T_board_avg) / Power | Fixed T=300K on all outer walls |
| Theta-JC | (T_die_max - T_case) / Power | Fixed T=300K on thermal_paste_top only, all others adiabatic |

## Run

```
sim run workflows/flipchip_thermal/demo_flipchip_thermal.py --solver=fluent --json
```

## Skill migration path

This workflow script validates the setup on win1. Once proven, the patterns
(conduction-only thermal, BC switching, theta extraction) feed into a
"thermal characterization" task template in `skills/fluent-sim/SKILL.md`.
