"""Official Example 05 - Creating a node at CoG of every component (bumper.hm)

Adapted from: https://help.altair.com/hwdesktop/pythonapi/hypermesh/examples/hm_examples.html

Acceptance:
  - ok == True
  - n_components > 0
  - n_cog_nodes == n_components (one node created per component)
  - all CoG coordinates are valid (not NaN)
"""
import json
import traceback
import hm
import hm.entities as ent
import os

OUT = "E:/simcli/sim-skills/hypermesh/base/workflows/official_examples/ex05_result.json"

try:
    model = hm.Model()
    model.hm_answernext("yes")

    modelfile = os.path.join(hm.altair_home, "demos/hm/bumper.hm")
    model.readfile(modelfile, 0)

    # Create material and property
    mat1 = ent.Material(model)
    mat1.name = "Al"
    mat1.cardimage = "MAT1"
    mat1.E = 7e04
    mat1.Nu = 0.3
    mat1.Rho = 2700

    prop1 = ent.Property(model)
    prop1.name = "central_prop"
    prop1.cardimage = "PSHELL"
    prop1.materialid = mat1
    prop1.PSHELL_T = 1.0

    # Collection of all components
    comp_col = hm.Collection(model, ent.Component)
    n_components = len(comp_col)

    cog_data = []
    n_cog_nodes = 0

    for comp in comp_col:
        comp.propertyid = prop1
        ccol = hm.Collection([comp])
        status, cog_result = model.hm_getcog(ccol)
        coord = list(cog_result.coord)
        nodeNew = ent.Node(model)
        nodeNew.localcoordinates = cog_result.coord
        cog_data.append({
            "comp_id": comp.id,
            "comp_name": comp.name,
            "cog": coord,
            "node_id": nodeNew.id,
        })
        n_cog_nodes += 1

    result = {
        "ok": True,
        "example": "05_cog_nodes",
        "model_file": "bumper.hm",
        "n_components": n_components,
        "n_cog_nodes": n_cog_nodes,
        "cog_nodes": cog_data[:5],  # first 5 for brevity
    }
    with open(OUT, "w") as f:
        json.dump(result, f, indent=2)

except Exception as e:
    with open(OUT, "w") as f:
        json.dump({"ok": False, "error": str(e)}, f)
    with open(OUT.replace(".json", "_traceback.txt"), "w") as f:
        traceback.print_exc(file=f)
