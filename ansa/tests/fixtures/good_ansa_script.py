"""Example ANSA batch script — prints model info as JSON."""
import json
import ansa
from ansa import base, session, constants


def main():
    """Entry point for ansa64.bat -execscript."""
    info = session.ApplicationInformation(format="text")
    result = {
        "step": "hello",
        "app_info": info[:200] if info else "unknown",
        "ok": True,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
