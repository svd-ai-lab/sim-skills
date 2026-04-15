"""MAPDL 2D Beam — Tier A vendor verification example.

Source: https://mapdl.docs.pyansys.com/version/stable/examples/gallery_examples/00-mapdl-examples/mapdl_beam.html

An I-beam with BEAM188 elements, simply supported at the two ends,
with a central point load. Published in "Finite Element Analysis
Using ANSYS 11.0" (Chaitanya et al., 2010).

Runs via:
    sim run workflows/mapdl_beam/scripts/run.py --solver mapdl

Acceptance:
  - exit_code == 0
  - JSON output has ok=True
  - Static analysis converges (solve returns non-error)
  - Vertical displacement at mid-span (node 12) is negative (downward)
  - Displacement magnitude in a physically plausible range for steel
    I-beam under 22.84 kN load over 2.20 m span
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import numpy as np
from ansys.mapdl.core import launch_mapdl

# Output location for evidence PNGs — relative to script dir
OUT = Path(__file__).resolve().parent.parent / "evidence"
OUT.mkdir(exist_ok=True)

mapdl = launch_mapdl(loglevel="ERROR", run_location=str(OUT))

try:
    # ---- Phase 1: PREP7 --------------------------------------------------
    mapdl.prep7()
    mapdl.et(1, "BEAM188")
    mapdl.keyopt(1, 4, 1)                    # transverse shear output

    # Material — steel-like, in cm-N units per the vendor example
    mapdl.mp("EX", 1, 2e7)                   # N/cm^2 (20e6 = 200 GPa)
    mapdl.mp("PRXY", 1, 0.27)

    # I-beam section
    mapdl.sectype(1, "BEAM", "I", "ISection", 3)
    mapdl.secoffset("CENT")
    mapdl.secdata(15, 15, 29, 2, 2, 1)       # flange+web dims in cm

    # Nodes along 220 cm span
    mapdl.n(1, 0, 0, 0)
    mapdl.n(12, 110, 0, 0)
    mapdl.n(23, 220, 0, 0)
    mapdl.fill(1, 12, 10)
    mapdl.fill(12, 23, 10)

    # Elements between consecutive nodes
    for node in mapdl.mesh.nnum[:-1]:
        mapdl.e(int(node), int(node) + 1)

    n_nodes = len(mapdl.mesh.nnum)
    n_elems = len(mapdl.mesh.enum)

    # BCs: constrain UX, UY, ROTX, ROTZ on all; UZ only on supports
    for const in ("UX", "UY", "ROTX", "ROTZ"):
        mapdl.d("all", const)
    mapdl.d(1, "UZ")
    mapdl.d(23, "UZ")

    # Apply -Z force at mid-span (node 12)
    load = -22840.0     # N
    mapdl.f(12, "FZ", load)

    mapdl.finish()

    # ---- Phase 2: SOLU --------------------------------------------------
    mapdl.slashsolu()
    mapdl.antype("STATIC")
    solve_out = mapdl.solve()
    mapdl.finish()

    # ---- Phase 3: POST1 -------------------------------------------------
    mapdl.post1()
    mapdl.set(1, 1)

    uz = mapdl.post_processing.nodal_displacement("Z")
    ux = mapdl.post_processing.nodal_displacement("X")

    max_deflection = float(uz.min())     # most negative UZ (downward)
    max_abs_disp = float(np.max(np.abs(uz)))

    # Save mesh + deformed-shape PNG (headless)
    try:
        mapdl.post_processing.plot_nodal_displacement(
            "Z",
            savefig=str(OUT / "mapdl_beam_disp_z.png"),
            off_screen=True,
            window_size=(1200, 700),
            cmap="viridis",
            show_edges=True,
        )
        png_disp = "mapdl_beam_disp_z.png"
    except Exception as e:
        png_disp = f"plot_failed:{e.__class__.__name__}"

    mapdl.finish()

finally:
    mapdl.exit()

# Physics-based acceptance
ok = (
    max_deflection < 0.0            # deflects downward
    and 0.0 < max_abs_disp < 1.0    # within 1 cm (sane for 2.20 m beam)
)

print(json.dumps({
    "ok": ok,
    "n_nodes": n_nodes,
    "n_elements": n_elems,
    "applied_load_N": load,
    "mid_span_node": 12,
    "max_abs_disp_cm": max_abs_disp,
    "max_deflection_cm_signed": max_deflection,
    "png": png_disp,
}))
