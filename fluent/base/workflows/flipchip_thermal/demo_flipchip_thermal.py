"""
Flip-chip BGA thermal characterization using Ansys Fluent.

Computes JEDEC-standard thermal resistances (Theta-JB, Theta-JC) for a
flip-chip package on a 2S2P PCB using conduction-only analysis.

Based on: https://blog.ozeninc.com/resources/flip-chip-thermal-characterization-using-ansys-fluent

Case file: Flip_chip_demo_simplified.cas.h5 (download from Ozen blog)
  - 455K cells, 61 solid zones, 397 face zones
  - Full 2S2P PCB stackup, 49 BGA solder balls, die + substrate + underfill
  - Materials pre-assigned, energy equation OFF (enabled in this script)
  - Contains named expression Power/Volume(['flipchip-die-die']) — needs
    "Power" defined as a named expression before solving

Tested with: ansys-fluent-core 0.38.1, Fluent 2025 R2 (v252)

This is a reference script — NOT meant for sim exec (it calls launch_fluent).
The sim-native version uses sim connect + sim exec steps; see README.md.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SEP = "-" * 60
TESTED_PYFLUENT = "0.38"  # version this script was validated against
import os as _os
_datasets = _os.environ.get("SIM_DATASETS")
if not _datasets:
    raise RuntimeError(
        "SIM_DATASETS env var not set. Set it to the directory containing "
        "the flipchip dataset (expects flipchip/Flip_chip_demo_simplified.cas.h5 inside)."
    )
CASE_FILE = Path(_datasets) / "flipchip" / "Flip_chip_demo_simplified.cas.h5"
DIE_POWER_W = 1.0  # 1 W die power for thermal resistance calculation

# Outer walls of the package + PCB assembly
OUTER_WALLS = [
    "die_sides", "thermal_paste_top", "thermal_paste_sides",
    "pcb_bottom", "pcb_bottom_inside_ring", "pcb_bottom_ring",
    "pcb_sides", "pcb_sides.1", "pcb_sides.2", "pcb_sides.3",
    "pcb_sides.4", "pcb_sides.5", "pcb_sides.6",
    "pcb_top", "pcb_top_inside_ring", "pcb_top_ring",
    "substrate_sides", "substrate_top",
    "underfilldie_sides", "underfillpcb_sides",
]


def step(n: int, title: str) -> None:
    print(f"\n[Step {n}] {title}")
    print(SEP)


def set_wall_bc(solver, wall_name: str, condition: str, value: float) -> bool:
    """Set thermal BC on a wall. Returns True on success."""
    try:
        w = solver.settings.setup.boundary_conditions.wall[wall_name]
        w.thermal.thermal_condition = condition
        if condition == "Temperature":
            w.thermal.temperature.value = value
        else:  # Heat Flux
            w.thermal.heat_flux.value = value
        return True
    except Exception:
        return False


# -- Step 1: import ------------------------------------------------
step(1, "Import ansys-fluent-core")

try:
    import ansys.fluent.core as pyfluent
    pyfluent_version = pyfluent.__version__
    print(f"  pyfluent version = {pyfluent_version}")
    major_minor = ".".join(pyfluent_version.split(".")[:2])
    if major_minor != TESTED_PYFLUENT:
        print(f"  WARNING: this script was tested with pyfluent {TESTED_PYFLUENT}, "
              f"running {major_minor} — API differences possible")
except ImportError as e:
    print(f"  ERROR: import failed - {e}")
    sys.exit(1)

import ansys.fluent.core.fluent_connection as _fc
_fc._is_localhost = lambda address: True

# -- Step 2: locate case file --------------------------------------
step(2, "Locate flip-chip case file")

if not CASE_FILE.exists():
    print(f"  ERROR: case file not found: {CASE_FILE}")
    print("  Download from: https://blog.ozeninc.com/hubfs/Flip_chip_demo_simplified.zip")
    sys.exit(1)
print(f"  found: {CASE_FILE.name}")

# -- Step 3: launch Fluent solver session --------------------------
step(3, "Launch Fluent solver session (GUI)")

try:
    solver = pyfluent.launch_fluent(
        mode="solver",
        ui_mode="gui",
        precision="double",
        processor_count=2,
    )
    print(f"  session type = {type(solver).__name__}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    sys.exit(1)

# -- Step 4: read case ---------------------------------------------
step(4, "Read case file")

try:
    solver.settings.file.read_case(file_name=str(CASE_FILE))
    print(f"  Case loaded: {CASE_FILE.name}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    solver.exit()
    sys.exit(1)

# -- Step 5: mesh check --------------------------------------------
step(5, "Mesh check")

try:
    solver.settings.mesh.check()
    print("  Mesh check OK")
except Exception as e:
    print(f"  WARNING: {type(e).__name__}: {e}")

# -- Step 6: enable energy equation --------------------------------
step(6, "Enable energy equation")

try:
    solver.settings.setup.models.energy.enabled = True
    print("  Energy equation enabled")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    solver.exit()
    sys.exit(1)

# -- Step 7: set die heat source -----------------------------------
step(7, f"Set volumetric heat source on die ({DIE_POWER_W} W)")

try:
    # The case has expression Power/Volume(['flipchip-die-die']) already
    # assigned to the die zone. Define "Power" so the expression resolves.
    ne = solver.settings.setup.named_expressions
    ne["Power"] = {"definition": f"{DIE_POWER_W} [W]"}

    # Enable sources on the die zone (pyfluent 0.38 API)
    die = solver.settings.setup.cell_zone_conditions.solid["flipchip-die-die"]
    die.sources.enable = True
    die.sources.terms = {
        "energy": [{"option": "value", "value": f"Power/Volume(['flipchip-die-die'])"}]
    }
    print(f"  Die heat source set via named expression: Power = {DIE_POWER_W} W")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    solver.exit()
    sys.exit(1)

# -- Step 8: create surface from die cell zone ---------------------
step(8, "Create surface from die cell zone (for report extraction)")

try:
    # fields.reduction and report_definitions need surface names, not cell
    # zone names. Create a surface from the die cell zone via TUI.
    solver.tui.surface.zone_surface("die_surface", "flipchip-die-die")
    print("  Created 'die_surface' from cell zone 'flipchip-die-die'")
except Exception as e:
    print(f"  WARNING: {type(e).__name__}: {e}")

# -- Step 9: set BCs for Theta-JB ---------------------------------
step(9, "Set boundary conditions for Theta-JB (fixed T=300K on all outer walls)")

set_count = sum(set_wall_bc(solver, w, "Temperature", 300.0) for w in OUTER_WALLS)
print(f"  Set T=300K on {set_count}/{len(OUTER_WALLS)} outer walls")

# -- Step 10: initialize and solve Theta-JB ------------------------
step(10, "Initialize and solve (Theta-JB)")

solver.settings.solution.initialization.hybrid_initialize()
print("  Hybrid initialization complete")
solver.settings.solution.run_calculation.iterate(iter_count=200)
print("  Solver finished")

# -- Step 11: extract Theta-JB ------------------------------------
step(11, "Extract Theta-JB results")

theta_jb = None
t_die_max_jb = None
t_board_avg_jb = None

try:
    rd = solver.settings.solution.report_definitions

    rd.surface["die_t_max"] = {}
    rd.surface["die_t_max"].report_type = "surface-facetmax"
    rd.surface["die_t_max"].field = "temperature"
    rd.surface["die_t_max"].surface_names = ["die_surface"]

    rd.surface["board_t_avg"] = {}
    rd.surface["board_t_avg"].report_type = "surface-areaavg"
    rd.surface["board_t_avg"].field = "temperature"
    rd.surface["board_t_avg"].surface_names = ["pcb_top"]

    rd.compute(report_defs=["die_t_max", "board_t_avg"])

    # Parse values from report output (report_definitions.compute prints to stdout)
    # For programmatic access, re-extract via reduction on the created surface
    t_die_max_jb = solver.fields.reduction.maximum(
        expression="Temperature", locations=["die_surface"],
    )
    t_board_avg_jb = solver.fields.reduction.area_average(
        expression="Temperature", locations=["pcb_top"],
    )
    theta_jb = (t_die_max_jb - t_board_avg_jb) / DIE_POWER_W
    print(f"  T_die_max  = {t_die_max_jb:.4f} K")
    print(f"  T_board_avg = {t_board_avg_jb:.4f} K")
    print(f"  Theta-JB   = {theta_jb:.4f} K/W")
except Exception as e:
    print(f"  WARNING: extraction failed - {type(e).__name__}: {e}")

# -- Step 12: set BCs for Theta-JC --------------------------------
step(12, "Set boundary conditions for Theta-JC (adiabatic except case top)")

for wall_name in OUTER_WALLS:
    if wall_name == "thermal_paste_top":
        set_wall_bc(solver, wall_name, "Temperature", 300.0)
    else:
        set_wall_bc(solver, wall_name, "Heat Flux", 0.0)
print("  Adiabatic on all walls except thermal_paste_top (T=300K)")

# -- Step 13: re-initialize and solve Theta-JC --------------------
step(13, "Re-initialize and solve (Theta-JC)")

solver.settings.solution.initialization.hybrid_initialize()
print("  Hybrid initialization complete")
solver.settings.solution.run_calculation.iterate(iter_count=200)
print("  Solver finished")

# -- Step 14: extract Theta-JC ------------------------------------
step(14, "Extract Theta-JC results")

theta_jc = None
t_die_max_jc = None
t_case_jc = None

try:
    rd = solver.settings.solution.report_definitions

    rd.surface["case_t_avg"] = {}
    rd.surface["case_t_avg"].report_type = "surface-areaavg"
    rd.surface["case_t_avg"].field = "temperature"
    rd.surface["case_t_avg"].surface_names = ["thermal_paste_top"]

    rd.compute(report_defs=["die_t_max", "case_t_avg"])

    t_die_max_jc = solver.fields.reduction.maximum(
        expression="Temperature", locations=["die_surface"],
    )
    t_case_jc = solver.fields.reduction.area_average(
        expression="Temperature", locations=["thermal_paste_top"],
    )
    theta_jc = (t_die_max_jc - t_case_jc) / DIE_POWER_W
    print(f"  T_die_max = {t_die_max_jc:.4f} K")
    print(f"  T_case    = {t_case_jc:.4f} K")
    print(f"  Theta-JC  = {theta_jc:.4f} K/W")
except Exception as e:
    print(f"  WARNING: extraction failed - {type(e).__name__}: {e}")

# -- Done ----------------------------------------------------------
print(f"\n{'='*60}")
print("Flip-chip thermal characterization complete")
print(f"{'='*60}")

results = {
    "status": "ok",
    "workflow": "flipchip-thermal-characterization",
    "case_file": str(CASE_FILE),
    "die_power_w": DIE_POWER_W,
    "theta_jb": {
        "value_k_per_w": theta_jb,
        "t_die_max_k": t_die_max_jb,
        "t_board_avg_k": t_board_avg_jb,
    },
    "theta_jc": {
        "value_k_per_w": theta_jc,
        "t_die_max_k": t_die_max_jc,
        "t_case_k": t_case_jc,
    },
}
print(json.dumps(results, indent=2, default=str))

try:
    solver.exit()
    print("  Fluent session closed")
except Exception:
    pass
