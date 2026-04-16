"""Step 4: Create a slice plane and export data as CSV.

Acceptance:
  - ok == True
  - n_points on slice > 0
  - CSV file created with expected columns

Run: sim run 04_slice_export.py --solver paraview -- /path/to/data.vtu z 0.5
"""
import json
import os
import sys

from paraview.simple import (
    OpenDataFile, Slice, Show, Render, ResetCamera,
    SaveData, UpdatePipeline, GetActiveView,
)


def main():
    if len(sys.argv) < 4:
        print(json.dumps({
            "ok": False,
            "error": "Usage: 04_slice_export.py <file> <axis> <position>",
        }))
        sys.exit(1)

    path = sys.argv[1]
    axis = sys.argv[2].lower()
    position = float(sys.argv[3])

    normal_map = {"x": [1, 0, 0], "y": [0, 1, 0], "z": [0, 0, 1]}
    if axis not in normal_map:
        print(json.dumps({"ok": False, "error": f"axis must be x/y/z, got {axis}"}))
        sys.exit(1)

    reader = OpenDataFile(path)
    if reader is None:
        print(json.dumps({"ok": False, "error": f"Cannot open: {path}"}))
        sys.exit(1)
    UpdatePipeline()

    normal = normal_map[axis]
    origin = [0, 0, 0]
    origin[{"x": 0, "y": 1, "z": 2}[axis]] = position

    sl = Slice(Input=reader)
    sl.SliceType = "Plane"
    sl.SliceType.Origin = origin
    sl.SliceType.Normal = normal
    UpdatePipeline()

    info = sl.GetDataInformation()
    n_points = info.GetNumberOfPoints()
    n_cells = info.GetNumberOfCells()

    result = {
        "ok": n_points > 0,
        "step": "slice-export",
        "axis": axis,
        "position": position,
        "slice_points": n_points,
        "slice_cells": n_cells,
    }

    # Export CSV
    try:
        out_csv = os.path.join(
            os.environ.get("TEMP", "/tmp"), "pv_slice.csv"
        )
        SaveData(out_csv, sl)
        result["csv_file"] = out_csv
        result["export"] = "ok"
    except Exception as e:
        result["export"] = f"failed: {e}"

    print(json.dumps(result))


if __name__ == "__main__":
    main()
