# MAPDL 2D I-beam via sim session mode (Phase 2).
# Vendor source: https://mapdl.docs.pyansys.com/.../mapdl_beam.html
#
# Incrementally builds the model through sim exec / inspect and
# captures every request + response into a transcript for evidence.

$ErrorActionPreference = "Stop"
$sim = "E:\simcli\sim-cli\.venv\Scripts\sim.exe"
$host_arg = "127.0.0.1"
$evidence = "E:\simcli\sim-skills\mapdl\base\workflows\mapdl_beam_session\evidence"
New-Item -ItemType Directory -Path $evidence -Force | Out-Null

$transcript = @()

function Invoke-Sim {
    param([string[]]$Args, [string]$Label)
    Write-Host "===== $Label =====" -ForegroundColor Cyan
    $argsWithHost = @("--host", $host_arg) + $Args
    $out = & $sim $argsWithHost 2>&1 | Out-String
    Write-Host $out
    $script:transcript += [PSCustomObject]@{
        step = $Label
        command = ("sim --host $host_arg " + ($Args -join ' '))
        response = $out.Trim()
        ts = (Get-Date).ToString("o")
    }
}

# Already connected from prior step — check session
Invoke-Sim -Args @("ps") -Label "ps-initial"

Invoke-Sim -Args @("inspect", "session.summary") -Label "inspect-session"

# Step 1: define element + material + section
$step1 = @'
mapdl.prep7()
mapdl.et(1, "BEAM188")
mapdl.keyopt(1, 4, 1)
mapdl.mp("EX", 1, 2e7)
mapdl.mp("PRXY", 1, 0.27)
mapdl.sectype(1, "BEAM", "I", "ISection", 3)
mapdl.secoffset("CENT")
mapdl.secdata(15, 15, 29, 2, 2, 1)
_result = {"step": "prep_setup", "ok": True}
'@
Invoke-Sim -Args @("exec", "--label", "prep_setup", $step1) -Label "exec-1-prep"

# Step 2: build nodes + elements
$step2 = @'
mapdl.n(1, 0, 0, 0); mapdl.n(12, 110, 0, 0); mapdl.n(23, 220, 0, 0)
mapdl.fill(1, 12, 10); mapdl.fill(12, 23, 10)
for nn in mapdl.mesh.nnum[:-1]:
    mapdl.e(int(nn), int(nn) + 1)
_result = {"nodes": int(len(mapdl.mesh.nnum)),
           "elems": int(len(mapdl.mesh.enum))}
'@
Invoke-Sim -Args @("exec", "--label", "build_mesh", $step2) -Label "exec-2-mesh"

Invoke-Sim -Args @("inspect", "mesh.summary") -Label "inspect-mesh"

# Step 3: BCs + load + solve
$step3 = @'
mapdl.finish(); mapdl.slashsolu()
for c in ("UX","UY","ROTX","ROTZ"):
    mapdl.d("all", c)
mapdl.d(1, "UZ"); mapdl.d(23, "UZ")
mapdl.f(12, "FZ", -22840.0)
mapdl.antype("STATIC")
mapdl.solve()
mapdl.finish()
_result = {"solved": True}
'@
Invoke-Sim -Args @("exec", "--label", "solve", $step3) -Label "exec-3-solve"

Invoke-Sim -Args @("inspect", "workdir.files") -Label "inspect-files-after-solve"

# Step 4: post + PNG
$png = "$evidence\session_mapdl_beam_uz.png"
$step4 = @"
import numpy as np
mapdl.post1(); mapdl.set(1, 1)
uz = mapdl.post_processing.nodal_displacement("Z")
mapdl.post_processing.plot_nodal_displacement(
    "Z",
    savefig=r"$png",
    off_screen=True,
    window_size=(1200, 700),
    cmap="viridis",
    show_edges=True,
)
_result = {"min_uz_cm": float(uz.min()),
           "max_abs_uz_cm": float(np.max(np.abs(uz))),
           "png": r"$png"}
"@
Invoke-Sim -Args @("exec", "--label", "post", $step4) -Label "exec-4-post"

Invoke-Sim -Args @("inspect", "last.result") -Label "inspect-last-result"

# Step 5: disconnect
Invoke-Sim -Args @("disconnect") -Label "disconnect"

# Save transcript
$transcript | ConvertTo-Json -Depth 4 | Set-Content "$evidence\transcript.json" -Encoding UTF8
Write-Host "`nTranscript saved to $evidence\transcript.json" -ForegroundColor Green
Write-Host "PNG saved to $png" -ForegroundColor Green
