# run_helpers.ps1 — shared functions for ANSA execution test scripts.
# Dot-source this file: . "$PSScriptRoot\run_helpers.ps1"

$env:PYTHONPATH = "E:\sim\sim\src"
$PYTHON = "python"
$ANSA_ROOT = "E:\Program Files (x86)\ANSA"
$ANSA_BAT = "$ANSA_ROOT\ansa_v25.0.0\ansa64.bat"
$FIXTURES = "E:\sim\sim-agent-ansa\tests\fixtures"
$AGENT_ROOT = "E:\sim\sim-agent-ansa"

function New-LogDir {
    param([string]$CaseId)
    $ts     = Get-Date -Format "yyyyMMdd_HHmmss"
    $logDir = "$AGENT_ROOT\tests\execution\logs\${CaseId}_${ts}"
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    return $logDir
}

function Write-Log {
    param([string]$LogFile, [string]$Message)
    $ts = Get-Date -Format "HH:mm:ss"
    $line = "$ts  $Message"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line
}

function Invoke-Driver {
    param(
        [string]$Code,
        [string]$LogFile,
        [string]$Label = ""
    )
    $header = @"
import sys, json
sys.path.insert(0, r'E:\sim\sim\src')
from pathlib import Path
from sim.drivers.ansa.driver import AnsaDriver
d = AnsaDriver()
try:
"@
    $footer = @"

except Exception as e:
    print(json.dumps({"error": str(e), "error_type": type(e).__name__}))
"@
    $indented = ($Code -split "`n" | ForEach-Object { "    $_" }) -join "`n"
    $fullCode = "$header`n$indented`n$footer"

    $tmpFile = [System.IO.Path]::GetTempFileName() -replace '\.tmp$', '.py'
    Set-Content -Path $tmpFile -Value $fullCode -Encoding UTF8
    $result = & $PYTHON $tmpFile 2>&1
    Remove-Item -Path $tmpFile -Force -ErrorAction SilentlyContinue
    if ($Label) { Write-Log $LogFile "  [$Label] $result" }
    try {
        return $result | ConvertFrom-Json -ErrorAction Stop
    } catch {
        if ($Label) { Write-Log $LogFile "  [$Label] RAW: $result" }
        return $null
    }
}

function Assert-Equal {
    param([string]$Field, $Actual, $Expected, [string]$LogFile)
    if ($Actual -eq $Expected) {
        Write-Log $LogFile "    PASS: $Field = $Actual"
        return $true
    } else {
        Write-Log $LogFile "    FAIL: $Field = $Actual (expected: $Expected)"
        return $false
    }
}

function Assert-True {
    param([string]$Field, $Value, [string]$LogFile)
    if ($Value) {
        Write-Log $LogFile "    PASS: $Field = True"
        return $true
    } else {
        Write-Log $LogFile "    FAIL: $Field = False (expected: True)"
        return $false
    }
}

function Assert-Contains {
    param([string]$Field, [string]$Haystack, [string]$Needle, [string]$LogFile)
    if ($Haystack -match [regex]::Escape($Needle)) {
        Write-Log $LogFile "    PASS: $Field contains '$Needle'"
        return $true
    } else {
        Write-Log $LogFile "    FAIL: $Field does not contain '$Needle'"
        return $false
    }
}
