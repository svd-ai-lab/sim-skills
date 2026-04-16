"""Step 3: Create iso-surface contour on a scalar field and render PNG.

Acceptance:
  - ok == True
  - contour has > 0 cells
  - screenshot file exists

Run: sim run 03_contour_render.py --solver paraview -- /path/to/data.vtu pressure 101325
"""
import json
import os
import sys

from paraview.simple import (
    OpenDataFile, Contour, Show, Hide, Render, ResetCamera,
    SaveScreenshot, GetActiveView, GetRepresentation,
    ColorBy, GetColorTransferFunction, UpdatePipeline,
)


def main():
    if len(sys.argv) < 4:
        print(json.dumps({
            "ok": False,
            "error": "Usage: 03_contour_render.py <file> <field> <value>",
        }))
        sys.exit(1)

    path = sys.argv[1]
    field = sys.argv[2]
    value = float(sys.argv[3])

    reader = OpenDataFile(path)
    if reader is None:
        print(json.dumps({"ok": False, "error": f"Cannot open: {path}"}))
        sys.exit(1)
    UpdatePipeline()

    contour = Contour(Input=reader)
    contour.ContourBy = ["POINTS", field]
    contour.Isosurfaces = [value]
    UpdatePipeline()

    info = contour.GetDataInformation()
    n_cells = info.GetNumberOfCells()
    n_points = info.GetNumberOfPoints()

    result = {
        "ok": n_cells > 0,
        "step": "contour-render",
        "field": field,
        "iso_value": value,
        "contour_cells": n_cells,
        "contour_points": n_points,
    }

    # Render
    try:
        Hide(reader)
        Show(contour)
        rep = GetRepresentation()
        ColorBy(rep, ("POINTS", field))
        lut = GetColorTransferFunction(field)
        lut.ApplyPreset("Viridis (matplotlib)", True)

        view = GetActiveView()
        view.ViewSize = [1920, 1080]
        ResetCamera()
        Render()

        out_png = os.path.join(
            os.environ.get("TEMP", "/tmp"), "pv_contour.png"
        )
        SaveScreenshot(out_png, ImageResolution=[1920, 1080])
        result["screenshot"] = out_png
        result["rendering"] = "ok"
    except Exception as e:
        result["rendering"] = f"failed: {e}"

    print(json.dumps(result))


if __name__ == "__main__":
    main()
