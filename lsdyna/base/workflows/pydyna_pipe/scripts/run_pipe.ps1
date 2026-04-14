# John Reid Pipe real E2E via sim CLI — session mode
#
# Rotating pipe with rigid bracket constraint. Demonstrates:
# - Multi-section shell + solid parts
# - SetPartList for grouping parts into contact/initial-velocity scopes
# - InitialVelocityGeneration with omega for angular velocity
# - DeformableToRigid switching for selected parts
# - ContactForceTransducerPenalty for force monitoring
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

Invoke-Sim -Subcommand "connect" -Args @("--solver", "ls_dyna") -Label "connect"

Invoke-Sim -Subcommand "exec" -Args @(
    "import shutil, os; src=r'$WorkDir\nodes.k'; dst=str(workdir / 'nodes.k'); shutil.copy(src, dst); _result = {'mesh_at': dst, 'size': os.path.getsize(dst)}"
) -Label "copy-mesh"

Invoke-Sim -Subcommand "exec" -Args @(
    "deck.title = 'Pipe — sim CLI session E2E'"
) -Label "title"

# Control cards
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.extend([kwd.ControlTermination(endtim=20.0), kwd.ControlEnergy(hgen=2, rwen=2, slnten=2), kwd.ControlOutput(npopt=1, neecho=3), kwd.ControlShell(istupd=1)])"
) -Label "control-cards"

# Database cards
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.extend([kwd.DatabaseBinaryD3Plot(dt=1.00), kwd.DatabaseExtentBinary(ieverp=1), kwd.DatabaseGlstat(dt=0.10), kwd.DatabaseMatsum(dt=0.10), kwd.DatabaseJntforc(dt=0.10), kwd.DatabaseRbdout(dt=0.10), kwd.DatabaseRcforc(dt=0.10)])"
) -Label "database-cards"

# Contact + force transducer
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.extend([kwd.ContactForceTransducerPenalty(surfa=1, surfatyp=3), kwd.ContactAutomaticSingleSurface(ssid=3, sstyp=2, fs=0.30, fd=0.30), kwd.SetPartList(sid=3, parts=[1, 2])])"
) -Label "contact"

# Initial angular velocity (omega) on parts 1 and 2
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.extend([kwd.InitialVelocityGeneration(id=5, omega=-0.082, xc=-78.50, yc=-610.13, zc=5.69, nx=1.0), kwd.SetPartList(sid=5, parts=[1, 2])])"
) -Label "initial-rotation"

# Pipe parts (3 parts via DataFrame)
Invoke-Sim -Subcommand "exec" -Args @(
    "import pandas as pd; pp = kwd.Part(); pp.parts = pd.DataFrame({'heading': ['Deformable-Pipe', 'Pipe-End', 'Rigid-Pipe'], 'pid': [1, 2, 3], 'secid': [1, 2, 2], 'mid': [1, 2, 1]}); deck.append(pp)"
) -Label "pipe-parts"

# Pipe materials and sections
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.extend([kwd.MatPlasticKinematic(mid=1, ro=7.86e-6, e=200.0, pr=0.30, sigy=0.250, etan=0.00689), kwd.MatRigid(mid=2, ro=7.86e-6, e=200.0, pr=0.30), kwd.SectionShell(secid=1, elfrom=2, nip=5, t1=11.0, t2=11.0, t3=11.0, t4=11.0), kwd.SectionShell(secid=2, elfrom=2, nip=3, t1=11.0, t2=11.0, t3=11.0, t4=11.0)])"
) -Label "pipe-materials"

# Bracket part + material
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.extend([kwd.Part(heading='Bracket', pid=4, secid=4, mid=4), kwd.MatRigid(mid=4, ro=7.86e-6, e=200.0, pr=0.30, cmo=1, con1=7, con2=7), kwd.SectionSolid(secid=4)])"
) -Label "bracket"

# Switch deformable parts to rigid (per official example)
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.extend([kwd.DeformableToRigid(pid=1), kwd.DeformableToRigid(pid=2)])"
) -Label "deformable-to-rigid"

# Include mesh
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.append(kwd.Include(filename='nodes.k'))"
) -Label "include-mesh"

Invoke-Sim -Subcommand "inspect" -Args @("deck.summary") -Label "inspect-deck"

Invoke-Sim -Subcommand "exec" -Args @(
    "deck.export_file(str(workdir / 'pipe.k'))"
) -Label "export-deck"

Write-Host "`n=== Solving (this takes ~15s) ===" -ForegroundColor Yellow
Invoke-Sim -Subcommand "exec" -Args @(
    "run_dyna('pipe.k', working_directory=str(workdir), stream=False)"
) -Label "solve"

Invoke-Sim -Subcommand "inspect" -Args @("workdir.files") -Label "inspect-files"
Invoke-Sim -Subcommand "inspect" -Args @("results.summary") -Label "inspect-results"

Invoke-Sim -Subcommand "exec" -Args @(
    "gke_op = dpf.operators.result.global_kinetic_energy(); gke_op.inputs.data_sources.connect(_data_sources); ke = gke_op.eval().get_field(0).data; gie_op = dpf.operators.result.global_internal_energy(); gie_op.inputs.data_sources.connect(_data_sources); ie = gie_op.eval().get_field(0).data; _result = {'n_states': len(ke), 'ke_max': float(max(ke)), 'ke_final': float(ke[-1]), 'ie_max': float(max(ie)), 'ie_final': float(ie[-1])}"
) -Label "extract-energies"

Invoke-Sim -Subcommand "exec" -Args @(
    "import numpy as np; disp_op = model.results.displacement.on_last_time_freq(); disp_field = disp_op.eval().get_field(0); disp_arr = np.asarray(disp_field.data).reshape(-1, 3); norms = np.linalg.norm(disp_arr, axis=1); _result = {'n_nodes': int(disp_arr.shape[0]), 'max_disp_mm': float(norms.max()), 'mean_disp_mm': float(norms.mean())}"
) -Label "extract-displacement"

$evidenceDir = "$WorkDir/evidence"
$pngScript = "$WorkDir/scripts/render_evidence.py"

Invoke-Sim -Subcommand "disconnect" -Label "disconnect"

$transcriptPath = "$evidenceDir/transcript.json"
$transcript | ConvertTo-Json -Depth 6 | Out-File -FilePath $transcriptPath -Encoding utf8
Write-Host "`n=== Saved transcript: $transcriptPath ===" -ForegroundColor Green

$copyMesh = $transcript | Where-Object { $_.label -eq "copy-mesh" } | Select-Object -First 1
if ($copyMesh -and $copyMesh.output -match "mesh_at':\s*'([^']+)") {
    $workdirPath = Split-Path $matches[1].Replace('\\', '\') -Parent
    Write-Host "Found workdir: $workdirPath"
    Write-Host "`n=== Rendering PNGs ==="
    & uv run python "$pngScript" "$workdirPath"
}
