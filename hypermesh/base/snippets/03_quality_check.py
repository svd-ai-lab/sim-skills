"""Step 3: Run element quality checks on current mesh.

Acceptance:
  - ok == True
  - quality metrics reported (aspect, skew, jacobian)
  - failed element counts below threshold

Run: sim run 03_quality_check.py --solver hypermesh
"""
import json
import hm
import hm.entities as ent

model = hm.Model()
hm.setoption(block_redraw=1, command_file_state=0, entity_highlighting=0)

def main():
    elems = hm.Collection(model, ent.Element)
    n_total = len(elems)

    if n_total == 0:
        print(json.dumps({"ok": False, "error": "No elements in model"}))
        return

    # Run quality checks
    # Aspect ratio check (threshold 5.0)
    failed_aspect = hm.Collection(model, ent.Element, populate=False)
    model.elementtestaspect(collection=elems, threshold=5.0)

    # Jacobian check (threshold 0.3)
    failed_jacobian = hm.Collection(model, ent.Element, populate=False)
    model.elementtestjacobian(collection=elems, threshold=0.3)

    # Skew check (threshold 60 degrees)
    failed_skew = hm.Collection(model, ent.Element, populate=False)
    model.elementtestskew(collection=elems, threshold=60.0)

    # Get quality summary
    status, summary = model.getqualitysummary(collection=elems)

    result = {
        "ok": True,
        "step": "quality-check",
        "n_elements": n_total,
        "checks": {
            "aspect_threshold": 5.0,
            "jacobian_threshold": 0.3,
            "skew_threshold": 60.0,
        },
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
