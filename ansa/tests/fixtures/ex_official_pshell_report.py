"""EX-12: Official PshellDataToText pattern — batch property report.

Based on BETA CAE's official scripts/Properties/PshellDataToText.py.
The official script collects all PSHELLs and reports PID, Name, T, MID1.

We adapt it for headless batch mode:
- No GUI file dialog (hardcoded output)
- Creates test properties first (empty model)
- Outputs JSON instead of text file
"""
import json
import ansa
from ansa import base, constants

def main():
    deck = constants.NASTRAN
    base.SetCurrentDeck(deck)

    # Create test data (official script assumes loaded model)
    mat = base.CreateEntity(deck, "MAT1", {
        "Name": "TestMaterial",
        "E": 210000.0,
        "NU": 0.3,
    })

    for name, t in [("Floor_2mm", 2.0), ("Roof_1mm", 1.0), ("Door_0.8mm", 0.8)]:
        base.CreateEntity(deck, "PSHELL", {
            "Name": name,
            "T": t,
            "MID1": mat._id if mat else 0,
        })

    # Official pattern: CollectEntities + GetEntityCardValues
    props = base.CollectEntities(deck, None, "PSHELL")
    report = []
    for prop in props:
        ret = base.GetEntityCardValues(deck, prop, ("PID", "Name", "T", "MID1"))
        report.append({
            "pid": ret.get("PID"),
            "name": ret.get("Name", ""),
            "thickness": ret.get("T"),
            "mid": ret.get("MID1"),
        })

    result = {
        "status": "ok",
        "source": "official_pshell_report_pattern",
        "property_count": len(report),
        "properties": report,
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
