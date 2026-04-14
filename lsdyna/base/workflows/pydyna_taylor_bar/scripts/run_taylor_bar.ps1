# Taylor Bar real E2E via sim CLI — session mode
#
# This script drives the official PyDyna Taylor Bar example through
# `sim connect/exec/inspect/disconnect`, recording every step's output.
#
# Prerequisites:
#   * sim serve running on $env:SIM_HOST : $env:SIM_PORT (defaults: 127.0.0.1:7700)
#   * ansys-dyna-core, ansys-dpf-core, matplotlib installed
#   * LS-DYNA + ANSYS install discoverable
#   * taylor_bar_mesh.k present in $WorkDir
#
# Usage:
#   pwsh -File run_taylor_bar.ps1
#
# Output:
#   * transcript.json   — every step's command + response
#   * energy_plot.png   — KE/IE time series via DPF
#   * stress_contour.png — final von Mises contour via DPF + PyVista

param(
    [string]$SimHost = "127.0.0.1",
    [int]$SimPort = 7700,
    [string]$WorkDir = (Resolve-Path "$PSScriptRoot/..").Path
)

$ErrorActionPreference = "Stop"
$transcript = @()

function Invoke-Sim {
    param(
        [Parameter(Mandatory=$true)] [string]$Subcommand,
        [string[]]$Args = @(),
        [string]$Label = ""
    )
    $cmdline = @("sim", "--host", $SimHost, "--port", $SimPort, $Subcommand) + $Args
    Write-Host "`n>> $($cmdline -join ' ')" -ForegroundColor Cyan
    $output = & uv run @cmdline 2>&1 | Out-String
    Write-Host $output
    $script:transcript += @{
        step = $script:transcript.Count + 1
        label = $Label
        command = $cmdline -join ' '
        output = $output.TrimEnd()
    }
    return $output
}

# --- Step 1: connect ----------------------------------------------------
Invoke-Sim -Subcommand "connect" -Args @("--solver", "ls_dyna") -Label "connect"

# --- Step 2: build deck via successive sim exec calls ------------------
$workdirEsc = $WorkDir.Replace('\', '/')

# Set up workdir and move mesh into it
Invoke-Sim -Subcommand "exec" -Args @(
    "import shutil, os; src=r'$WorkDir' + r'\taylor_bar_mesh.k'; dst=str(workdir / 'taylor_bar_mesh.k'); shutil.copy(src, dst); _result = {'mesh_at': dst, 'size': os.path.getsize(dst)}"
) -Label "copy-mesh"

# Title
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.title = 'Taylor Bar — sim CLI session E2E'"
) -Label "title"

# Material — MAT_PLASTIC_KINEMATIC (Mat003)
Invoke-Sim -Subcommand "exec" -Args @(
    "mat = kwd.Mat003(mid=1); mat.ro = 7.85e-9; mat.e = 150000.0; mat.pr = 0.34; mat.sigy = 390.0; mat.etan = 90.0; deck.append(mat)"
) -Label "material"

# Section
Invoke-Sim -Subcommand "exec" -Args @(
    "sec = kwd.SectionSolid(secid=1); sec.elform = 1; deck.append(sec)"
) -Label "section"

# Part
Invoke-Sim -Subcommand "exec" -Args @(
    "import pandas as pd; part = kwd.Part(); part.parts = pd.DataFrame({'pid': [1], 'mid': [1], 'secid': [1]}); deck.append(part)"
) -Label "part"

# Coordinate system
Invoke-Sim -Subcommand "exec" -Args @(
    "cs = kwd.DefineCoordinateSystem(cid=1); cs.xl = 1.0; cs.yp = 1.0; deck.append(cs)"
) -Label "coord-system"

# Initial velocity
Invoke-Sim -Subcommand "exec" -Args @(
    "iv = kwd.InitialVelocityGeneration(); iv.id = 1; iv.styp = 2; iv.vy = 300e3; iv.icid = 1; deck.append(iv)"
) -Label "initial-velocity"

# Define box for rigid wall node set
Invoke-Sim -Subcommand "exec" -Args @(
    "box = kwd.DefineBox(boxid=1, xmn=-500, xmx=500, ymn=39.0, ymx=40.1, zmn=-500, zmx=500); deck.append(box)"
) -Label "define-box"

# Node set
Invoke-Sim -Subcommand "exec" -Args @(
    "ns = kwd.SetNodeGeneral(); ns.sid = 1; ns.option = 'BOX'; ns.e1 = 1; deck.append(ns)"
) -Label "node-set"

# Rigid wall
Invoke-Sim -Subcommand "exec" -Args @(
    "rw = kwd.RigidwallPlanar(id=1); rw.nsid = 1; rw.yt = 40.1; rw.yh = 39.0; deck.append(rw)"
) -Label "rigid-wall"

# Control termination
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.append(kwd.ControlTermination(endtim=8.0e-5, dtmin=0.001))"
) -Label "control-termination"

# Database outputs
Invoke-Sim -Subcommand "exec" -Args @(
    "dt_out = 8.0e-8; deck.extend([kwd.DatabaseGlstat(dt=dt_out, binary=3), kwd.DatabaseMatsum(dt=dt_out, binary=3), kwd.DatabaseNodout(dt=dt_out, binary=3), kwd.DatabaseElout(dt=dt_out, binary=3), kwd.DatabaseRwforc(dt=dt_out, binary=3), kwd.DatabaseBinaryD3Plot(dt=4.0e-6)])"
) -Label "database-outputs"

# Include the mesh file
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.append(kwd.Include(filename='taylor_bar_mesh.k'))"
) -Label "include-mesh"

# --- Step 3: inspect deck before solve ---------------------------------
Invoke-Sim -Subcommand "inspect" -Args @("deck.summary") -Label "inspect-deck"

# --- Step 4: write .k file and solve -----------------------------------
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.export_file(str(workdir / 'taylor_bar.k'))"
) -Label "export-deck"

Invoke-Sim -Subcommand "inspect" -Args @("workdir.files") -Label "inspect-files-before-solve"

Write-Host "`n=== Solving (this takes ~60s) ===" -ForegroundColor Yellow
Invoke-Sim -Subcommand "exec" -Args @(
    "run_dyna('taylor_bar.k', working_directory=str(workdir), stream=False)"
) -Label "solve"

# --- Step 5: verify and post-process via DPF ---------------------------
Invoke-Sim -Subcommand "inspect" -Args @("workdir.files") -Label "inspect-files-after-solve"
Invoke-Sim -Subcommand "inspect" -Args @("results.summary") -Label "inspect-results"

# Extract kinetic energy time series
Invoke-Sim -Subcommand "exec" -Args @(
    "gke_op = dpf.operators.result.global_kinetic_energy(); gke_op.inputs.data_sources.connect(_data_sources); ke = gke_op.eval().get_field(0).data; _result = {'ke_initial': float(ke[0]), 'ke_max': float(max(ke)), 'ke_final': float(ke[-1]), 'n_states': len(ke)}"
) -Label "extract-kinetic-energy"

# Extract internal energy
Invoke-Sim -Subcommand "exec" -Args @(
    "gie_op = dpf.operators.result.global_internal_energy(); gie_op.inputs.data_sources.connect(_data_sources); ie = gie_op.eval().get_field(0).data; _result = {'ie_initial': float(ie[0]), 'ie_max': float(max(ie)), 'ie_final': float(ie[-1])}"
) -Label "extract-internal-energy"

# Extract max final displacement
Invoke-Sim -Subcommand "exec" -Args @(
    "import numpy as np; disp_op = model.results.displacement.on_last_time_freq(); disp_field = disp_op.eval().get_field(0); disp_arr = np.asarray(disp_field.data).reshape(-1, 3); norms = np.linalg.norm(disp_arr, axis=1); _result = {'max_disp_mm': float(norms.max()), 'mean_disp_mm': float(norms.mean()), 'n_nodes': int(disp_arr.shape[0])}"
) -Label "extract-displacement"

# Render PNG visualizations using a separate Python script (PyVista needs more setup)
$evidenceDir = "$WorkDir/evidence"
$pngScript = "$WorkDir/scripts/render_evidence.py"
Write-Host "`n=== Rendering evidence PNGs ===" -ForegroundColor Yellow
Invoke-Sim -Subcommand "exec" -Args @(
    "import subprocess, sys, json; r = subprocess.run([sys.executable, r'$pngScript', str(workdir)], capture_output=True, text=True); _result = {'returncode': r.returncode, 'stdout_tail': r.stdout[-500:], 'stderr_tail': r.stderr[-500:]}"
) -Label "render-pngs"

# --- Step 6: disconnect -------------------------------------------------
Invoke-Sim -Subcommand "disconnect" -Label "disconnect"

# --- Save transcript ----------------------------------------------------
$transcriptPath = "$evidenceDir/transcript.json"
$transcript | ConvertTo-Json -Depth 6 | Out-File -FilePath $transcriptPath -Encoding utf8
Write-Host "`n=== Saved transcript: $transcriptPath ===" -ForegroundColor Green
Write-Host "Total steps: $($transcript.Count)"

# Extract the session workdir from the copy-mesh entry and render PNGs
$copyMesh = $transcript | Where-Object { $_.label -eq "copy-mesh" } | Select-Object -First 1
if ($copyMesh -and $copyMesh.output -match "mesh_at':\s*'([^']+)") {
    $workdirPath = Split-Path $matches[1].Replace('\\', '\') -Parent
    Write-Host "Found workdir: $workdirPath"
    Write-Host "`n=== Rendering PNGs ==="
    & uv run python "$pngScript" "$workdirPath"
} else {
    Write-Host "Could not extract workdir from transcript" -ForegroundColor Red
}
