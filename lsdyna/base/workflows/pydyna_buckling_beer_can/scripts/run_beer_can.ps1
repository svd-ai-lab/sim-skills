# Beer Can Buckling real E2E via sim CLI — implicit nonlinear analysis
#
# Highly nonlinear thin-shell buckling of an aluminum can under axial load.
# Demonstrates:
# - Implicit dynamics control cards
# - ContactAutomaticSingleSurfaceMortar (modern explicit/implicit standard)
# - SectionShell with elform=-16 (shell with extra precision)
# - Large BC and load arrays loaded from JSON helper
# - Atypical convergence: solver may not fully converge — that IS the result

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

# Copy mesh + BC data into workdir
Invoke-Sim -Subcommand "exec" -Args @(
    "import shutil, os; src=r'$WorkDir\mesh.k'; dst=str(workdir / 'mesh.k'); shutil.copy(src, dst); shutil.copy(r'$WorkDir\scripts\bc_data.json', str(workdir / 'bc_data.json')); _result = {'mesh_size': os.path.getsize(dst)}"
) -Label "copy-files"

Invoke-Sim -Subcommand "exec" -Args @(
    "deck.title = 'Beer Can Buckling — sim CLI session E2E'"
) -Label "title"

# Mortar contact (the new standard)
Invoke-Sim -Subcommand "exec" -Args @(
    "ca = kwd.ContactAutomaticSingleSurfaceMortar(cid=1); ca.options['ID'].active = True; ca.heading = 'Single-Surface Mortar Contact'; deck.append(ca)"
) -Label "contact-mortar"

# Implicit control cards
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.extend([kwd.ControlAccuracy(iacc=1), kwd.ControlImplicitAuto(iauto=1, dtmax=0.01), kwd.ControlImplicitDynamics(imass=1, gamma=0.6, beta=0.38), kwd.ControlImplicitGeneral(imflag=1, dt0=0.01), kwd.ControlImplicitSolution(nlprint=2), kwd.ControlShell(esort=2, theory=-16, intgrd=1, nfail4=1, irquad=0), kwd.ControlTermination(endtim=1.0)])"
) -Label "implicit-control"

# Database
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.extend([kwd.DatabaseGlstat(dt=1.0e-4, binary=3, ioopt=0), kwd.DatabaseSpcforc(dt=1e-4, binary=3, ioopt=0), kwd.DatabaseBinaryD3Plot(dt=1.0e-4), kwd.DatabaseExtentBinary(maxint=-3, nintsld=1)])"
) -Label "database"

# Parts, materials, sections
Invoke-Sim -Subcommand "exec" -Args @(
    "can_part = kwd.Part(heading='Beer Can', pid=1, secid=1, mid=1, eosid=0); floor_part = kwd.Part(heading='Floor', pid=2, secid=2, mid=1); mat = kwd.MatElastic(mid=1, ro=2.59e-4, e=1.0e7, pr=0.33, title='Aluminum'); mat.options['TITLE'].active = True; can_shell = kwd.SectionShell(secid=1, elform=-16, shrf=0.8333, nip=3, t1=0.002, propt=0.0, title='Beer Can'); can_shell.options['TITLE'].active = True; floor_shell = kwd.SectionShell(secid=2, elform=-16, shrf=0.833, t1=0.01, propt=0.0); floor_shell.options['TITLE'].active = True; floor_shell.title = 'Floor'; deck.extend([can_part, can_shell, floor_part, floor_shell, mat])"
) -Label "parts-materials"

# Load curve
Invoke-Sim -Subcommand "exec" -Args @(
    "import pandas as pd; lc = kwd.DefineCurve(lcid=1, curves=pd.DataFrame({'a1': [0.00, 1.00], 'o1': [0.0, 1.000]})); lc.options['TITLE'].active = True; lc.title = 'Load vs. Time'; deck.append(lc)"
) -Label "load-curve"

# Load and BC — load from JSON helper (76 load nodes, 152 BC nodes)
Invoke-Sim -Subcommand "exec" -Args @(
    "import json, pandas as pd, numpy as np; bcdata = json.loads((workdir / 'bc_data.json').read_text()); load_nodes = bcdata['load_nodes']; n = len(load_nodes); zeros = np.zeros(n); load = kwd.LoadNodePoint(nodes=pd.DataFrame({'nid': load_nodes, 'dof': np.full((n), 3), 'lcid': np.full((n), 1), 'sf': np.full((n), -13.1579), 'cid': zeros, 'm1': zeros, 'm2': zeros, 'm3': zeros})); deck.append(load); _result = {'n_load_nodes': n}"
) -Label "load-points"

Invoke-Sim -Subcommand "exec" -Args @(
    "import json, pandas as pd, numpy as np; bcdata = json.loads((workdir / 'bc_data.json').read_text()); nid = bcdata['bc_nid']; dofz = bcdata['bc_dofz']; n = len(nid); zeros = np.zeros(n); ones = np.full((n), 1); bc = kwd.BoundarySpcNode(nodes=pd.DataFrame({'nid': nid, 'cid': zeros, 'dofx': ones, 'dofy': ones, 'dofz': dofz, 'dofrx': ones, 'dofry': ones, 'dofrz': ones})); deck.append(bc); _result = {'n_bc_nodes': n}"
) -Label "boundary-conditions"

# Include mesh
Invoke-Sim -Subcommand "exec" -Args @(
    "deck.append(kwd.Include(filename='mesh.k'))"
) -Label "include-mesh"

Invoke-Sim -Subcommand "inspect" -Args @("deck.summary") -Label "inspect-deck"

Invoke-Sim -Subcommand "exec" -Args @(
    "deck.export_file(str(workdir / 'beer_can.k'))"
) -Label "export-deck"

Write-Host "`n=== Solving (this is implicit nonlinear, may take a few minutes) ===" -ForegroundColor Yellow
Invoke-Sim -Subcommand "exec" -Args @(
    "run_dyna('beer_can.k', working_directory=str(workdir), stream=False)"
) -Label "solve"

Invoke-Sim -Subcommand "inspect" -Args @("workdir.files") -Label "inspect-files"
Invoke-Sim -Subcommand "inspect" -Args @("results.summary") -Label "inspect-results"

# Energy extraction
Invoke-Sim -Subcommand "exec" -Args @(
    "gke_op = dpf.operators.result.global_kinetic_energy(); gke_op.inputs.data_sources.connect(_data_sources); ke = gke_op.eval().get_field(0).data; gie_op = dpf.operators.result.global_internal_energy(); gie_op.inputs.data_sources.connect(_data_sources); ie = gie_op.eval().get_field(0).data; _result = {'n_states': len(ke), 'ke_max': float(max(ke)), 'ke_final': float(ke[-1]), 'ie_max': float(max(ie)), 'ie_final': float(ie[-1])}"
) -Label "extract-energies"

# Displacement
Invoke-Sim -Subcommand "exec" -Args @(
    "import numpy as np; disp_op = model.results.displacement.on_last_time_freq(); disp_field = disp_op.eval().get_field(0); disp_arr = np.asarray(disp_field.data).reshape(-1, 3); norms = np.linalg.norm(disp_arr, axis=1); _result = {'n_nodes': int(disp_arr.shape[0]), 'max_disp': float(norms.max()), 'mean_disp': float(norms.mean())}"
) -Label "extract-displacement"

$evidenceDir = "$WorkDir/evidence"
$pngScript = "$WorkDir/scripts/render_evidence.py"

Invoke-Sim -Subcommand "disconnect" -Label "disconnect"

$transcriptPath = "$evidenceDir/transcript.json"
$transcript | ConvertTo-Json -Depth 6 | Out-File -FilePath $transcriptPath -Encoding utf8
Write-Host "`n=== Saved transcript: $transcriptPath ===" -ForegroundColor Green

$copyMesh = $transcript | Where-Object { $_.label -eq "copy-files" } | Select-Object -First 1
if ($copyMesh -and $copyMesh.output -match "mesh_size") {
    # Workdir is in the previous step's output - extract from inspect-files instead
    $inspectFiles = $transcript | Where-Object { $_.label -eq "inspect-files" } | Select-Object -First 1
    if ($inspectFiles -and $inspectFiles.output -match '"workdir":\s*"([^"]+)"') {
        $workdirPath = $matches[1].Replace('\\', '\')
        Write-Host "Found workdir: $workdirPath"
        Write-Host "`n=== Rendering PNGs ==="
        & uv run python "$pngScript" "$workdirPath"
    }
}
