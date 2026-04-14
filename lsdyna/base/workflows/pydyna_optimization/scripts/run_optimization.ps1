# Plate Thickness Optimization real E2E via sim CLI
#
# Iterative parametric sweep: vary plate thickness, run LS-DYNA each time,
# extract max plate displacement via DPF, decide whether target met.
#
# This demonstrates the *parametric study* pattern: one connect, one helpers
# load, then loop with sim exec triggering each iteration. Each iteration is
# a one-shot LS-DYNA solve, but the surrounding optimizer state persists.
#
# We do 4 iterations (instead of the official 20) to keep test time reasonable.

param(
    [string]$SimHost = "127.0.0.1",
    [int]$SimPort = 7700,
    [string]$WorkDir = (Resolve-Path "$PSScriptRoot/..").Path,
    [int]$MaxIterations = 4,
    [double]$InitialThickness = 0.1,
    [double]$ThicknessIncrement = 0.5,
    [double]$TargetDisplacement = 1.0
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

# --- Step 2: load helpers (defines create_input_deck, run_iteration) ---
$helpersPath = "$WorkDir\scripts\opt_helpers.py".Replace('\', '/')
# Pass globals() explicitly so def's land in the session namespace.
# Force UTF-8 (Windows GBK default chokes on em-dashes in docstring).
Invoke-Sim -Subcommand "exec" -Args @(
    "_g = globals(); exec(open(r'$helpersPath', encoding='utf-8').read(), _g); _result = {'helpers_loaded': True, 'fns': sorted([n for n in _g if n.startswith(('create_', 'write_', 'run_iter'))])}"
) -Label "load-helpers"

# --- Step 3: stage mesh source path -------------------------------------
$meshSrc = "$WorkDir\bar_impact_mesh.k".Replace('\', '/')
Invoke-Sim -Subcommand "exec" -Args @(
    "MESH_SRC = r'$meshSrc'; _result = {'mesh_src': MESH_SRC}"
) -Label "stage-mesh-src"

# --- Step 4: parametric loop --------------------------------------------
Write-Host "`n=== Parametric sweep: $MaxIterations iterations ===" -ForegroundColor Yellow

for ($i = 0; $i -lt $MaxIterations; $i++) {
    $thickness = $InitialThickness + $ThicknessIncrement * $i
    $thicknessStr = "{0:F4}" -f $thickness

    Write-Host "`n--- Iteration ${i}: thickness = $thicknessStr ---" -ForegroundColor Magenta

    $code = "import os; case_dir = str(workdir / f'thickness_{$thicknessStr}'); _result = run_iteration($thicknessStr, case_dir, MESH_SRC)"
    Invoke-Sim -Subcommand "exec" -Args @($code) -Label "iter-$i-thickness-$thicknessStr"

    Invoke-Sim -Subcommand "inspect" -Args @("last.result") -Label "iter-$i-result"
}

# --- Step 5: collect all results -----------------------------------------
Invoke-Sim -Subcommand "exec" -Args @(
    "import os; results = []; [results.append({'thickness': float(d.replace('thickness_', '')), 'wd': str(workdir / d)}) for d in os.listdir(str(workdir)) if d.startswith('thickness_')]; _result = {'n_runs': len(results), 'thicknesses': sorted([r['thickness'] for r in results])}"
) -Label "collect-runs"

# --- Step 6: disconnect -------------------------------------------------
$evidenceDir = "$WorkDir/evidence"
$pngScript = "$WorkDir/scripts/render_evidence.py"

Invoke-Sim -Subcommand "disconnect" -Label "disconnect"

# --- Save transcript ----------------------------------------------------
$transcriptPath = "$evidenceDir/transcript.json"
$transcript | ConvertTo-Json -Depth 6 | Out-File -FilePath $transcriptPath -Encoding utf8
Write-Host "`n=== Saved transcript: $transcriptPath ===" -ForegroundColor Green

# --- Find session workdir + render evidence -----------------------------
# Workdir comes from any iter result line
$iter0 = $transcript | Where-Object { $_.label -like "iter-0-thickness*" } | Select-Object -First 1
if ($iter0 -and $iter0.output -match "'wd': '([^']+)") {
    $caseDir = $matches[1].Replace('\\', '\')
    $sessionWd = Split-Path $caseDir -Parent
    Write-Host "Session workdir: $sessionWd"
    Write-Host "`n=== Rendering PNGs ==="
    & uv run python "$pngScript" "$sessionWd"
} else {
    Write-Host "Could not extract workdir" -ForegroundColor Red
}
