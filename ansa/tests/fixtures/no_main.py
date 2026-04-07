"""ANSA script without main() — will trigger a warning."""
import ansa
from ansa import base, constants

shells = base.CollectEntities(constants.NASTRAN, None, "SHELL", False)
print(f"Found {len(shells)} shells")
