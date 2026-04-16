"""Step 2: Import geometry and generate surface mesh.

Acceptance:
  - ok == True
  - n_elements > 0
  - n_nodes > 0

Run: sim run 02_import_and_mesh.py --solver hypermesh -- /path/to/geometry.step
"""
import json
import sys
import hm
import hm.entities as ent

model = hm.Model()
hm.setoption(block_redraw=1, command_file_state=0, entity_highlighting=0)
model.hm_blockbrowserupdate(mode=1)

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "error": "Usage: script.py <geometry_file>"}))
        return

    geom_file = sys.argv[1]

    # Pre-answer popups
    model.hm_answernext('yes')

    # Import geometry
    hm.setoption_cadreader("step", "TargetUnits", "MMKS (mm kg N s)")
    status = model.geomimport(filename=geom_file)

    # Count surfaces
    surfaces = hm.Collection(model, ent.Surface)
    n_surfaces = len(surfaces)

    # Set mesh parameters
    hm.setoption(element_size=5.0, element_order=1)

    # Automesh surfaces
    status = model.automesh(collection=surfaces)

    # Count results
    nodes = hm.Collection(model, ent.Node)
    elems = hm.Collection(model, ent.Element)

    result = {
        "ok": len(elems) > 0,
        "step": "import-and-mesh",
        "file": geom_file,
        "n_surfaces": n_surfaces,
        "n_nodes": len(nodes),
        "n_elements": len(elems),
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
