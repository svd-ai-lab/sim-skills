"""Runner: execute all official examples sequentially, take screenshots.

Launch in HyperMesh via: run "E:/simcli/sim-skills/hypermesh/base/workflows/official_examples/run_all.py"
Or via: runhwx.exe ... -f run_all.py
"""
import json
import os
import traceback

BASEDIR = "E:/simcli/sim-skills/hypermesh/base/workflows/official_examples"
SCRIPTS = [
    "ex01_create_entities.py",
    "ex02_modify_entities.py",
    "ex05_cog_nodes.py",
    "ex06_solid_components.py",
]

summary = []

for script_name in SCRIPTS:
    script_path = os.path.join(BASEDIR, script_name)
    result_path = script_path.replace(".py", "_result.json")

    # Remove old result
    if os.path.exists(result_path):
        os.remove(result_path)

    print(f"\n=== Running {script_name} ===")
    try:
        exec(open(script_path).read())
        # Read result
        if os.path.exists(result_path):
            with open(result_path) as f:
                result = json.load(f)
            print(f"  Result: ok={result.get('ok')}")
            summary.append({"script": script_name, "result": result})
        else:
            summary.append({"script": script_name, "result": {"ok": False, "error": "no result file"}})
    except Exception as e:
        print(f"  Error: {e}")
        summary.append({"script": script_name, "result": {"ok": False, "error": str(e)}})

# Write summary
with open(os.path.join(BASEDIR, "e2e_summary.json"), "w") as f:
    json.dump({
        "test_date": "2026-04-17",
        "hypermesh_version": "2026.0.0.27",
        "total": len(SCRIPTS),
        "passed": sum(1 for s in summary if s["result"].get("ok")),
        "results": summary,
    }, f, indent=2)

print(f"\n=== Summary: {sum(1 for s in summary if s['result'].get('ok'))}/{len(SCRIPTS)} passed ===")
