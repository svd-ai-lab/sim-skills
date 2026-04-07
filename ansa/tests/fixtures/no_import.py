"""Python script that does NOT import ansa — should not be detected."""
import json


def main():
    print(json.dumps({"status": "this is not an ANSA script"}))
