"""Step 4: Export solver deck (OptiStruct/Nastran).

Acceptance:
  - ok == True
  - output file created
  - file size > 0

Run: sim run 04_export_deck.py --solver hypermesh -- output.fem optistruct
"""
import json
import os
import sys
import hm
import hm.entities as ent

model = hm.Model()
hm.setoption(block_redraw=1, command_file_state=0, entity_highlighting=0)

def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "ok": False,
            "error": "Usage: script.py <output_file> <template>",
        }))
        return

    output_file = sys.argv[1]
    template = sys.argv[2]  # optistruct, nastran, abaqus, lsdyna, radioss

    # Export
    status = model.feoutputwithdata(
        template=template,
        filename=output_file,
    )

    exists = os.path.isfile(output_file)
    size_kb = os.path.getsize(output_file) / 1024.0 if exists else 0

    # Count exported entities
    nodes = hm.Collection(model, ent.Node)
    elems = hm.Collection(model, ent.Element)

    result = {
        "ok": exists and size_kb > 0,
        "step": "export-deck",
        "template": template,
        "output_file": output_file,
        "file_exists": exists,
        "file_size_kb": round(size_kb, 1),
        "n_nodes": len(nodes),
        "n_elements": len(elems),
        "status": status.status,
        "message": status.message,
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
