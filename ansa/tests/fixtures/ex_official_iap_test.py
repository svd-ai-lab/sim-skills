"""EX-11: Official IAP test script pattern.

Based on BETA CAE's official test_script_ansa.py from
scripts/RemoteControl/ansa_examples/test_script_ansa.py.

The official script returns {'A':'0', 'B':'1', 'C':'2'}.
We extend it with JSON output for sim parse_output() compatibility.
"""
import json

def main():
    # Official BETA CAE test pattern: return a string dict
    official_result = {'A': '0', 'B': '1', 'C': '2'}

    # sim-compatible JSON output
    result = {
        "status": "ok",
        "source": "official_iap_test_pattern",
        "official_return": official_result,
    }
    print(json.dumps(result))

    # Also return the dict (IAP protocol expects this)
    return official_result
