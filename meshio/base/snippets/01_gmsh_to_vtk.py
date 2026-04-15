"""Step 1: Gmsh .msh → VTK .vtk conversion (verified E2E).

Acceptance:
  - Read succeeds
  - Round-trip VTK preserves point count
  - Output: {ok, points, total_cells, cells_by_type, points_match}

Run:
  sim run 01_gmsh_to_vtk.py --solver meshio
  (input: sphere.msh must exist in cwd; generate with Gmsh first)
"""
import json
import sys
import meshio


def main():
    inp = sys.argv[1] if len(sys.argv) > 1 else "sphere.msh"
    out = sys.argv[2] if len(sys.argv) > 2 else "sphere.vtk"

    mesh = meshio.read(inp)
    meshio.write(out, mesh)

    # Round-trip verification
    mesh_rt = meshio.read(out)
    result = {
        "ok": True,
        "input": inp,
        "output": out,
        "points": len(mesh.points),
        "total_cells": sum(len(c.data) for c in mesh.cells),
        "cells_by_type": {c.type: len(c.data) for c in mesh.cells},
        "roundtrip_points": len(mesh_rt.points),
        "points_match": len(mesh.points) == len(mesh_rt.points),
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
