"""Step 1: Smoke test -- create model, material, property, report.

Acceptance:
  - ok == True
  - material created with correct E and Nu
  - property created with correct thickness

Run: sim run 01_smoke_test.py --solver hypermesh
"""
import json
import hm
import hm.entities as ent

model = hm.Model()

# Suppress GUI for batch
hm.setoption(block_redraw=1, command_file_state=0, entity_highlighting=0)

def main():
    # Create material
    mat = ent.Material(model)
    mat.name = "Steel"
    mat.cardimage = "MAT1"
    mat.E = 2.1e5
    mat.Nu = 0.3
    mat.Rho = 7.85e-9

    # Create property
    prop = ent.Property(model)
    prop.name = "Shell_2mm"
    prop.cardimage = "PSHELL"
    prop.materialid = mat
    prop.PSHELL_T = 2.0

    # Query
    mats = hm.Collection(model, ent.Material)
    props = hm.Collection(model, ent.Property)

    result = {
        "ok": True,
        "step": "smoke-test",
        "n_materials": len(mats),
        "n_properties": len(props),
        "material_name": mat.name,
        "E": mat.E,
        "Nu": mat.Nu,
        "thickness": prop.PSHELL_T,
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
