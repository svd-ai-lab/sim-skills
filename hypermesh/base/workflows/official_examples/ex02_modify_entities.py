"""Official Example 02 - Modifying existing entities (bumper.hm)

Adapted from: https://help.altair.com/hwdesktop/pythonapi/hypermesh/examples/hm_examples.html

Acceptance:
  - ok == True
  - material E == 210000.0
  - material Nu == 0.3
  - element isolated (element 18 exists)
"""
import json
import traceback
import hm
import hm.entities as ent
import os

OUT = "E:/simcli/sim-skills/hypermesh/base/workflows/official_examples/ex02_result.json"

try:
    model = hm.Model()
    model.hm_answernext("yes")

    modelfile = os.path.join(hm.altair_home, "demos/hm/bumper.hm")
    model.readfile(modelfile, 0)

    # Retrieve material ID 1 and update properties
    mat1 = ent.Material(model, 1)
    mat_name_before = mat1.name
    mat1.cardimage = "MAT1"
    mat1.E = 2.1e+05
    mat1.Nu = 0.3

    # Retrieve element ID 18 and isolate it
    elem = ent.Element(model, 18)
    model.isolateonlyentity(elem)

    result = {
        "ok": True,
        "example": "02_modify_entities",
        "model_file": "bumper.hm",
        "mat_name": mat_name_before,
        "mat_E": mat1.E,
        "mat_Nu": mat1.Nu,
        "element_18_config": elem.config,
    }
    with open(OUT, "w") as f:
        json.dump(result, f, indent=2)

except Exception as e:
    with open(OUT, "w") as f:
        json.dump({"ok": False, "error": str(e)}, f)
    with open(OUT.replace(".json", "_traceback.txt"), "w") as f:
        traceback.print_exc(file=f)
