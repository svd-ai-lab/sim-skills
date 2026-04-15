"""Step 1: read a mesh, compute surface area and volume (verified E2E).

Acceptance (unit sphere):
  - surface_area ≈ 4π (12.566) within 15%
  - volume      ≈ 4π/3 (4.189) within 15%
  - Observed (Gmsh MeshSize=0.2): 12.47 area (0.76% err), 4.13 volume (1.37% err)

Run: sim run 01_sphere_stats.py --solver pyvista
"""
import json
import math
import sys

import pyvista as pv


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "sphere.vtu"
    grid = pv.read(path)

    surface = grid.extract_surface()
    surf_area = float(surface.area)

    sized = grid.compute_cell_sizes(length=False, area=False, volume=True)
    total_volume = float(sized.cell_data["Volume"].sum())

    result = {
        "ok": True,
        "step": "mesh-stats",
        "file": path,
        "n_points": int(grid.n_points),
        "n_cells": int(grid.n_cells),
        "bounds": list(map(float, grid.bounds)),
        "surface_area": surf_area,
        "volume": total_volume,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
