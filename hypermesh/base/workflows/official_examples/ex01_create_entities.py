"""Official Example 01 - Creating new entities (bumper.hm)

Adapted from: https://help.altair.com/hwdesktop/pythonapi/hypermesh/examples/hm_examples.html

Acceptance:
  - ok == True
  - n_nodes > 0 (bumper model loaded)
  - new_node_id > 0 (node created)
  - material_name == "Steel"
"""
import json
import traceback
import hm
import hm.entities as ent
import os

OUT = "E:/simcli/sim-skills/hypermesh/base/workflows/official_examples/ex01_result.json"

try:
    model = hm.Model()
    model.hm_answernext("yes")

    # Reading a HyperMesh database file
    modelfile = os.path.join(hm.altair_home, "demos/hm/bumper.hm")
    model.readfile(modelfile, 0)

    # Collection of all nodes
    node_col = hm.Collection(model, ent.Node)
    n_nodes = len(node_col)

    # Create a node
    node = ent.Node(model)
    new_node_id = node.id

    # Create a material and name it 'Steel'
    mat1 = ent.Material(model)
    mat1.name = "Steel"
    mat1.cardimage = "MAT1"

    # Count elements too
    elem_col = hm.Collection(model, ent.Element)
    n_elements = len(elem_col)

    # Count components
    comp_col = hm.Collection(model, ent.Component)
    n_components = len(comp_col)

    result = {
        "ok": True,
        "example": "01_create_entities",
        "model_file": "bumper.hm",
        "n_nodes": n_nodes,
        "n_elements": n_elements,
        "n_components": n_components,
        "new_node_id": new_node_id,
        "material_name": mat1.name,
        "material_cardimage": mat1.cardimage,
    }
    with open(OUT, "w") as f:
        json.dump(result, f, indent=2)

except Exception as e:
    with open(OUT, "w") as f:
        json.dump({"ok": False, "error": str(e)}, f)
    with open(OUT.replace(".json", "_traceback.txt"), "w") as f:
        traceback.print_exc(file=f)
