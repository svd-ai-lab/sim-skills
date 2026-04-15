"""Phase 2 session E2E — MAPDL 2D I-beam via sim connect/exec/inspect.

Runs outside the sim venv. Uses `sim.exe --host 127.0.0.1 <cmd>` and
saves a transcript JSON + a PNG to evidence/.
"""
from __future__ import annotations

import datetime
import json
import subprocess
from pathlib import Path

SIM = r"E:\simcli\sim-cli\.venv\Scripts\sim.exe"
HOST = "127.0.0.1"
EVIDENCE = Path(r"E:\simcli\sim-skills\mapdl\base\workflows\mapdl_beam_session\evidence")
EVIDENCE.mkdir(parents=True, exist_ok=True)

transcript: list[dict] = []


def call(label: str, *args: str, input_text: str | None = None) -> str:
    """Run `sim.exe --host HOST <args>`; append to transcript; return stdout."""
    cmd = [SIM, "--host", HOST, *args]
    print(f"===== {label} =====")
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    print(out.strip())
    transcript.append({
        "step": label,
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "response": out.strip(),
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
    })
    return out


# Step 0: status
call("ps-initial", "ps")
call("inspect-session", "inspect", "session.summary")

# Step 1: PREP7 — element, material, section
STEP1 = '''mapdl.prep7()
mapdl.et(1, "BEAM188")
mapdl.keyopt(1, 4, 1)
mapdl.mp("EX", 1, 2e7)
mapdl.mp("PRXY", 1, 0.27)
mapdl.sectype(1, "BEAM", "I", "ISection", 3)
mapdl.secoffset("CENT")
mapdl.secdata(15, 15, 29, 2, 2, 1)
_result = {"step": "prep_setup", "ok": True}'''
call("exec-1-prep", "exec", "--label", "prep_setup", STEP1)

# Step 2: nodes + elements
STEP2 = '''mapdl.n(1, 0, 0, 0); mapdl.n(12, 110, 0, 0); mapdl.n(23, 220, 0, 0)
mapdl.fill(1, 12, 10); mapdl.fill(12, 23, 10)
for nn in mapdl.mesh.nnum[:-1]:
    mapdl.e(int(nn), int(nn) + 1)
_result = {"nodes": int(len(mapdl.mesh.nnum)),
           "elems": int(len(mapdl.mesh.enum))}'''
call("exec-2-mesh", "exec", "--label", "build_mesh", STEP2)
call("inspect-mesh", "inspect", "mesh.summary")

# Step 3: BCs + solve
STEP3 = '''mapdl.finish(); mapdl.slashsolu()
for c in ("UX","UY","ROTX","ROTZ"):
    mapdl.d("all", c)
mapdl.d(1, "UZ"); mapdl.d(23, "UZ")
mapdl.f(12, "FZ", -22840.0)
mapdl.antype("STATIC")
mapdl.solve()
mapdl.finish()
_result = {"solved": True}'''
call("exec-3-solve", "exec", "--label", "solve", STEP3)
call("inspect-files-after-solve", "inspect", "workdir.files")

# Step 4: post — PNG + scalars
PNG = EVIDENCE / "session_mapdl_beam_uz.png"
STEP4 = f'''import numpy as np
mapdl.post1(); mapdl.set(1, 1)
uz = mapdl.post_processing.nodal_displacement("Z")
mapdl.post_processing.plot_nodal_displacement(
    "Z",
    savefig=r"{PNG}",
    off_screen=True,
    window_size=(1200, 700),
    cmap="viridis",
    show_edges=True,
)
_result = {{"min_uz_cm": float(uz.min()),
           "max_abs_uz_cm": float(np.max(np.abs(uz))),
           "png": r"{PNG}"}}'''
call("exec-4-post", "exec", "--label", "post", STEP4)
call("inspect-last-result", "inspect", "last.result")

# Step 5: teardown
call("disconnect", "disconnect")

# Save transcript
with open(EVIDENCE / "transcript.json", "w", encoding="utf-8") as f:
    json.dump(transcript, f, indent=2, ensure_ascii=False)

print()
print(f"Transcript: {EVIDENCE / 'transcript.json'}")
print(f"PNG:        {PNG}")
print(f"Steps:      {len(transcript)}")
