"""Step 2: Load a data file and report array names, bounds, cell/point counts.

Acceptance:
  - ok == True
  - n_points > 0
  - arrays list is non-empty (for real simulation data)

Run: sim run 02_load_and_stats.py --solver paraview -- /path/to/data.vtu
"""
import json
import sys

from paraview.simple import OpenDataFile, UpdatePipeline


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "error": "Usage: 02_load_and_stats.py <file>"}))
        sys.exit(1)

    path = sys.argv[1]
    reader = OpenDataFile(path)
    if reader is None:
        print(json.dumps({"ok": False, "error": f"Cannot open: {path}"}))
        sys.exit(1)

    UpdatePipeline()
    info = reader.GetDataInformation()

    # Point arrays
    point_arrays = []
    pi = info.GetPointDataInformation()
    for i in range(pi.GetNumberOfArrays()):
        arr = pi.GetArrayInformation(i)
        name = arr.GetName()
        nc = arr.GetNumberOfComponents()
        ranges = []
        for c in range(nc):
            lo, hi = arr.GetComponentRange(c)
            ranges.append([lo, hi])
        point_arrays.append({
            "name": name, "components": nc, "ranges": ranges,
        })

    # Cell arrays
    cell_arrays = []
    ci = info.GetCellDataInformation()
    for i in range(ci.GetNumberOfArrays()):
        arr = ci.GetArrayInformation(i)
        name = arr.GetName()
        nc = arr.GetNumberOfComponents()
        ranges = []
        for c in range(nc):
            lo, hi = arr.GetComponentRange(c)
            ranges.append([lo, hi])
        cell_arrays.append({
            "name": name, "components": nc, "ranges": ranges,
        })

    result = {
        "ok": True,
        "step": "load-and-stats",
        "file": path,
        "n_points": info.GetNumberOfPoints(),
        "n_cells": info.GetNumberOfCells(),
        "bounds": list(info.GetBounds()),
        "point_arrays": point_arrays,
        "cell_arrays": cell_arrays,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
