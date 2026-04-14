# John Reid Pendulum real E2E via sim CLI — session mode
#
# Multi-rigid-body pendulum: two spheres on elastic beam wires under gravity.
# Initial velocity given to one sphere via *INITIAL_VELOCITY+box selection.
# Demonstrates: BoundarySpcNode, DeformableToRigid, ContactAutomaticSingleSurface,
#              LoadBodyY (gravity), multi-part decks via DataFrame.

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

# --- Step 2: copy mesh into session workdir -----------------------------
Invoke-Sim -Subcommand "exec" -Args @(
    "import shutil, os; src=r'$WorkDir\nodes.k'; dst=str(workdir / 'nodes.k'); shutil.copy(src, dst); _result = {'mesh_at': dst, 'size': os.path.getsize(dst)}"
) -Label "copy-mesh"

# --- Step 3: build deck via successive sim exec calls ------------------

# Title
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.title = 'Pendulum — sim CLI session E2E'"
) -Label "title"

# Control cards
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.extend([kwd.ControlTermination(endtim=11.0), kwd.ControlEnergy(hgen=2, rwen=2), kwd.ControlOutput(npopt=1, neecho=3), kwd.ControlShell(istupd=1, theory=2)])"
) -Label "control-cards"

# Database cards
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.extend([kwd.DatabaseBinaryD3Plot(dt=1.00), kwd.DatabaseExtentBinary(ieverp=1), kwd.DatabaseGlstat(dt=0.10), kwd.DatabaseMatsum(dt=0.10), kwd.DatabaseNodout(dt=0.10), kwd.DatabaseHistoryNode(id1=350, id2=374, id3=678, id4=713), kwd.DatabaseRbdout(dt=0.10), kwd.DatabaseRcforc(dt=0.10)])"
) -Label "database-cards"

# Contact + gravity
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.extend([kwd.ContactAutomaticSingleSurface(ssid=0, fs=0.08, fd=0.08), kwd.ControlContact(shlthk=2)])"
) -Label "contact"

# Gravity load (LoadBodyY references curve lcid=1)
Invoke-Sim -Subcommand "exec" -Args @(
    "import pandas as pd; curve1 = kwd.DefineCurve(lcid=1); curve1.curves = pd.DataFrame({'a1': [0.00, 10000.00], 'o1': [1.000, 1.000]}); deck.extend([kwd.LoadBodyY(lcid=1, sf=0.00981), curve1])"
) -Label "gravity-load"

# Boundary conditions — fix wire anchor nodes
Invoke-Sim -Subcommand "exec" -Args @(
    "import pandas as pd; bc = kwd.BoundarySpcNode(); bc.nodes = pd.DataFrame({'nid': [45004, 45005, 45010, 45011], 'cid': [0, 0, 0, 0], 'dofx': [1, 1, 1, 1], 'dofy': [1, 1, 1, 1], 'dofz': [1, 1, 1, 1], 'dofrx': [0, 0, 0, 0], 'dofry': [0, 0, 0, 0], 'dofrz': [0, 0, 0, 0]}); deck.append(bc)"
) -Label "boundary-conditions"

# Initial velocity (via box selection)
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.extend([kwd.InitialVelocity(boxid=5, vx=0.0, vy=-12.0, vz=0.0), kwd.DefineBox(boxid=5, xmn=-120.0, xmx=-80.0, ymn=80.0, ymx=120.0, zmn=-30.0, zmx=30.0)])"
) -Label "initial-velocity-box"

# Parts (sphere parts via DataFrame, beam part single)
Invoke-Sim -Subcommand "exec" -Args @(
    "import pandas as pd; spherePart = kwd.Part(); spherePart.parts = pd.DataFrame({'heading': ['sphere1', 'sphere2'], 'pid': [1, 2], 'secid': [1, 2], 'mid': [1, 1]}); beamPart = kwd.Part(heading='Pendulum Wires - Elastic Beams', pid=45, secid=45, mid=45); deck.extend([spherePart, beamPart])"
) -Label "parts"

# Materials and sections
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.extend([kwd.MatPlasticKinematic(mid=1, ro=2.7e-6, e=68.9, pr=0.330, sigy=0.286, etan=0.00689), kwd.SectionShell(secid=1, elfrom=2, t1=1.0, t2=1.0, t3=1.0, t4=1.0), kwd.SectionShell(secid=2, elfrom=2, t1=1.0, t2=1.0, t3=1.0, t4=1.0), kwd.SectionBeam(secid=45, elform=3, shrf=1.00000, qr_irid=1.0, a=10.0), kwd.MatElastic(mid=45, ro=7.86e-6, e=210.0, pr=0.30)])"
) -Label "materials-sections"

# Switch sphere parts deformable -> rigid (to make them act as rigid balls)
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.extend([kwd.DeformableToRigid(pid=1), kwd.DeformableToRigid(pid=2)])"
) -Label "deformable-to-rigid"

# Include the mesh
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.append(kwd.Include(filename='nodes.k'))"
) -Label "include-mesh"

# --- Step 4: inspect deck before solve ---------------------------------
Invoke-Sim -Subcommand "inspect" -Args @("deck.summary") -Label "inspect-deck"

# --- Step 5: write .k file and solve -----------------------------------
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.export_file(str(workdir / 'pendulum.k'))"
) -Label "export-deck"

Write-Host "`n=== Solving (this takes ~10s) ===" -ForegroundColor Yellow
Invoke-Sim -Subcommand "exec" -Args @(
    "run_dyna('pendulum.k', working_directory=str(workdir), stream=False)"
) -Label "solve"

# --- Step 6: verify and post-process -----------------------------------
Invoke-Sim -Subcommand "inspect" -Args @("workdir.files") -Label "inspect-files"
Invoke-Sim -Subcommand "inspect" -Args @("results.summary") -Label "inspect-results"

# Extract energy time series
Invoke-Sim -Subcommand "exec" -Args @(
    "gke_op = dpf.operators.result.global_kinetic_energy(); gke_op.inputs.data_sources.connect(_data_sources); ke = gke_op.eval().get_field(0).data; gie_op = dpf.operators.result.global_internal_energy(); gie_op.inputs.data_sources.connect(_data_sources); ie = gie_op.eval().get_field(0).data; _result = {'n_states': len(ke), 'ke_max': float(max(ke)), 'ke_min': float(min(ke)), 'ke_final': float(ke[-1]), 'ie_max': float(max(ie)), 'ie_final': float(ie[-1])}"
) -Label "extract-energies"

# Extract maximum nodal displacement
Invoke-Sim -Subcommand "exec" -Args @(
    "import numpy as np; disp_op = model.results.displacement.on_last_time_freq(); disp_field = disp_op.eval().get_field(0); disp_arr = np.asarray(disp_field.data).reshape(-1, 3); norms = np.linalg.norm(disp_arr, axis=1); _result = {'n_nodes': int(disp_arr.shape[0]), 'max_disp_mm': float(norms.max()), 'mean_disp_mm': float(norms.mean())}"
) -Label "extract-displacement"

# Extract sphere-1 trajectory (node 350 — history node)
Invoke-Sim -Subcommand "exec" -Args @(
    "import numpy as np; coord_op = model.results.coordinates; positions = []; tfs = model.metadata.time_freq_support; n = len(tfs.time_frequencies.data_as_list); _result = {'n_history_states': n}"
) -Label "extract-trajectory-meta"

# Render PNG evidence (DPF + matplotlib)
$evidenceDir = "$WorkDir/evidence"
$pngScript = "$WorkDir/scripts/render_evidence.py"
Write-Host "`n=== Rendering evidence PNGs (subprocess) ===" -ForegroundColor Yellow

# --- Step 7: disconnect first to release DPF ---------------------------
Invoke-Sim -Subcommand "disconnect" -Label "disconnect"

# --- Save transcript ----------------------------------------------------
$transcriptPath = "$evidenceDir/transcript.json"
$transcript | ConvertTo-Json -Depth 6 | Out-File -FilePath $transcriptPath -Encoding utf8
Write-Host "`n=== Saved transcript: $transcriptPath ===" -ForegroundColor Green
Write-Host "Total steps: $($transcript.Count)"

# Extract the session workdir from the copy-mesh transcript entry
$copyMesh = $transcript | Where-Object { $_.label -eq "copy-mesh" } | Select-Object -First 1
if ($copyMesh -and $copyMesh.output -match "mesh_at':\s*'([^']+)") {
    $workdirPath = Split-Path $matches[1].Replace('\\', '\') -Parent
    Write-Host "Found workdir: $workdirPath"
    Write-Host "`n=== Rendering PNGs ==="
    & uv run python "$pngScript" "$workdirPath"
} else {
    Write-Host "Could not extract workdir from transcript" -ForegroundColor Red
}
