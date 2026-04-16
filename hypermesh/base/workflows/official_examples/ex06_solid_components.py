"""Official Example 06 - Creating a new component per solid (bumper.hm)

Adapted from: https://help.altair.com/hwdesktop/pythonapi/hypermesh/examples/hm_examples.html
Includes the performance() optimization pattern.

Acceptance:
  - ok == True
  - Script runs without error
  - n_solids reported
"""
import json
import traceback
import hm
import hm.entities as ent
import os

OUT = "E:/simcli/sim-skills/hypermesh/base/workflows/official_examples/ex06_result.json"


def performance(model, switch):
    if switch:
        hm.setoption(
            block_redraw=1,
            command_file_state=0,
            entity_highlighting=0,
        )
        model.hm_blockbrowserupdate(mode=1)
    else:
        hm.setoption(
            block_redraw=0,
            command_file_state=1,
            entity_highlighting=1,
        )
        model.hm_blockbrowserupdate(mode=0)


try:
    model = hm.Model()
    model.hm_answernext("yes")

    modelfile = os.path.join(hm.altair_home, "demos/hm/bumper.hm")
    model.readfile(modelfile, 0)

    solidcol = hm.Collection(model, ent.Solid)
    n_solids = len(solidcol)

    # Enable performance boost
    performance(model, True)

    created_comps = []
    for solid in solidcol:
        comp = ent.Component(model)
        comp.name = f"solid_{solid.id}"
        solid_in_col = hm.Collection([solid])
        model.movemark(collection=solid_in_col, name=f"solid_{solid.id}")
        created_comps.append({"solid_id": solid.id, "comp_name": comp.name})

    # Disable performance boost
    performance(model, False)

    # Count final components
    final_comps = hm.Collection(model, ent.Component)

    result = {
        "ok": True,
        "example": "06_solid_components",
        "model_file": "bumper.hm",
        "n_solids": n_solids,
        "n_components_created": len(created_comps),
        "n_total_components": len(final_comps),
        "created": created_comps[:5],  # first 5 for brevity
    }
    with open(OUT, "w") as f:
        json.dump(result, f, indent=2)

except Exception as e:
    with open(OUT, "w") as f:
        json.dump({"ok": False, "error": str(e)}, f)
    with open(OUT.replace(".json", "_traceback.txt"), "w") as f:
        traceback.print_exc(file=f)
