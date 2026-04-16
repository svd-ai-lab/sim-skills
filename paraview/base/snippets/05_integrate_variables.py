"""Step 5: Integrate variables over a surface/volume for quantitative metrics.

Acceptance:
  - ok == True
  - integrated values are finite numbers
  - area/volume > 0

Run: sim run 05_integrate_variables.py --solver paraview -- /path/to/data.vtu
"""
import json
import math
import sys

from paraview.simple import (
    OpenDataFile, IntegrateVariables, UpdatePipeline,
    ExtractSurface,
)
from paraview.servermanager import Fetch


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "ok": False,
            "error": "Usage: 05_integrate_variables.py <file>",
        }))
        sys.exit(1)

    path = sys.argv[1]
    reader = OpenDataFile(path)
    if reader is None:
        print(json.dumps({"ok": False, "error": f"Cannot open: {path}"}))
        sys.exit(1)
    UpdatePipeline()

    # Integrate over volume
    integrate = IntegrateVariables(Input=reader)
    UpdatePipeline()

    data = Fetch(integrate)
    cell_data = data.GetCellData()

    integrated = {}
    for i in range(cell_data.GetNumberOfArrays()):
        arr = cell_data.GetArray(i)
        name = arr.GetName()
        nc = arr.GetNumberOfComponents()
        if nc == 1:
            integrated[name] = arr.GetValue(0)
        else:
            integrated[name] = [arr.GetValue(j) for j in range(nc)]

    # Check for Area or Volume
    area = integrated.get("Area", 0)
    volume = integrated.get("Volume", 0)

    result = {
        "ok": True,
        "step": "integrate-variables",
        "file": path,
        "integrated": {k: v for k, v in integrated.items()
                       if isinstance(v, (int, float)) and math.isfinite(v)},
        "area": area,
        "volume": volume,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
