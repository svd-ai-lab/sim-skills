"""Step 1: Smoke test — create a sphere, render PNG, report stats.

Acceptance:
  - ok == True
  - n_points > 0
  - n_cells > 0
  - screenshot file created (if rendering available)

Run: sim run 01_smoke_test.py --solver paraview
"""
import json
import os
import sys

from paraview.simple import (
    Sphere, Show, Render, ResetCamera, SaveScreenshot,
    GetActiveView, UpdatePipeline,
)


def main():
    sphere = Sphere(Radius=1.0, ThetaResolution=32, PhiResolution=32)
    UpdatePipeline()

    info = sphere.GetDataInformation()
    n_points = info.GetNumberOfPoints()
    n_cells = info.GetNumberOfCells()
    bounds = list(info.GetBounds())

    result = {
        "ok": True,
        "step": "smoke-test",
        "source": "Sphere",
        "n_points": n_points,
        "n_cells": n_cells,
        "bounds": bounds,
    }

    # Try rendering (may fail on headless without OSMesa)
    try:
        Show(sphere)
        view = GetActiveView()
        view.ViewSize = [800, 600]
        ResetCamera()
        Render()
        out_png = os.path.join(
            os.environ.get("TEMP", "/tmp"), "pv_smoke_test.png"
        )
        SaveScreenshot(out_png, ImageResolution=[800, 600])
        result["screenshot"] = out_png
        result["rendering"] = "ok"
    except Exception as e:
        result["rendering"] = f"failed: {e}"

    print(json.dumps(result))


if __name__ == "__main__":
    main()
