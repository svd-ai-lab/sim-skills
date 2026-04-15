"""Smoke test — launch MAPDL, print version, exit cleanly.

Runs via: sim run base/snippets/01_smoke_test.py --solver mapdl
Acceptance:
  - exit_code == 0
  - JSON output has ok=True and non-empty mapdl_version
"""
from __future__ import annotations

import json
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from ansys.mapdl.core import launch_mapdl

mapdl = launch_mapdl(loglevel="ERROR")
try:
    mapdl_version = str(mapdl.version)
    jobname = mapdl.jobname
finally:
    mapdl.exit()

print(json.dumps({
    "ok": True,
    "mapdl_version": mapdl_version,
    "jobname": jobname,
}))
