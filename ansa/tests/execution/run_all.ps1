# run_all.ps1 — Run all ANSA execution tests sequentially.
#
# Usage: powershell -ExecutionPolicy Bypass -File run_all.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\run_helpers.ps1"

$CASE_ID  = "ALL"
$LOG_DIR  = New-LogDir -CaseId $CASE_ID
$LOG_FILE = "$LOG_DIR\run.log"
$pass = 0; $fail = 0; $blocked = 0

Write-Log $LOG_FILE "=========================================="
Write-Log $LOG_FILE "  ANSA Execution Tests"
Write-Log $LOG_FILE "  Log dir: $LOG_DIR"
Write-Log $LOG_FILE "=========================================="

# -- EX-01: Connectivity -------------------------------------------------------
Write-Log $LOG_FILE ""
Write-Log $LOG_FILE "=== EX-01: Connectivity Check ==="

$r = Invoke-Driver -LogFile $LOG_FILE -Label "connect" -Code @"
info = d.connect()
print(json.dumps({"status": info.status, "version": info.version, "message": info.message}))
"@

$ok = $true
$ok = (Assert-Equal "status" $r.status "ok" $LOG_FILE) -and $ok
$ok = (Assert-Equal "version" $r.version "25.0.0" $LOG_FILE) -and $ok
$ok = (Assert-Contains "message" $r.message "ansa64.bat" $LOG_FILE) -and $ok

if ($ok) { $pass++; Write-Log $LOG_FILE "  EX-01: PASS" }
else     { $fail++; Write-Log $LOG_FILE "  EX-01: FAIL" }

# -- EX-02: Detection -----------------------------------------------------------
Write-Log $LOG_FILE ""
Write-Log $LOG_FILE "=== EX-02: Script Detection ==="

$r = Invoke-Driver -LogFile $LOG_FILE -Label "detect" -Code @"
results = {
    'good_script': d.detect(Path(r'$FIXTURES\good_ansa_script.py')),
    'no_import': d.detect(Path(r'$FIXTURES\no_import.py')),
    'gui_script': d.detect(Path(r'$FIXTURES\gui_script.py')),
}
print(json.dumps(results))
"@
$ok2 = Assert-True "detect good_script" $r.good_script $LOG_FILE
$ok2 = (Assert-Equal "detect no_import" $r.no_import $false $LOG_FILE) -and $ok2
$ok2 = (Assert-True "detect gui_script" $r.gui_script $LOG_FILE) -and $ok2

if ($ok2) { $pass++; Write-Log $LOG_FILE "  EX-02: PASS" }
else      { $fail++; Write-Log $LOG_FILE "  EX-02: FAIL" }

# -- EX-03: Linting -------------------------------------------------------------
Write-Log $LOG_FILE ""
Write-Log $LOG_FILE "=== EX-03: Script Linting ==="

$r = Invoke-Driver -LogFile $LOG_FILE -Label "lint" -Code @"
cases = {}
for name in ['good_ansa_script.py', 'no_import.py', 'syntax_error.py', 'no_main.py', 'gui_script.py']:
    lr = d.lint(Path(r'$FIXTURES' + '\\\\' + name))
    cases[name] = {'ok': lr.ok, 'diags': [x.message[:50] for x in lr.diagnostics]}
print(json.dumps(cases))
"@

$ok3 = Assert-True "lint good_ansa_script ok" $r.'good_ansa_script.py'.ok $LOG_FILE
$ok3 = (Assert-Equal "lint no_import ok" $r.'no_import.py'.ok $false $LOG_FILE) -and $ok3
$ok3 = (Assert-Equal "lint syntax_error ok" $r.'syntax_error.py'.ok $false $LOG_FILE) -and $ok3
$ok3 = (Assert-True "lint no_main ok" $r.'no_main.py'.ok $LOG_FILE) -and $ok3
$ok3 = (Assert-True "lint gui_script ok" $r.'gui_script.py'.ok $LOG_FILE) -and $ok3

if ($ok3) { $pass++; Write-Log $LOG_FILE "  EX-03: PASS" }
else      { $fail++; Write-Log $LOG_FILE "  EX-03: FAIL" }

# -- EX-04: Output Parsing ------------------------------------------------------
Write-Log $LOG_FILE ""
Write-Log $LOG_FILE "=== EX-04: Output Parsing ==="

$r = Invoke-Driver -LogFile $LOG_FILE -Label "parse" -Code @"
tests = [
    (d.parse_output(''), {}),
    (d.parse_output('no json'), {}),
    (d.parse_output('{\"count\": 42}'), {'count': 42}),
    (d.parse_output('line1\n{\"a\":1}\n{\"b\":2}'), {'b': 2}),
]
all_pass = all(a == e for a, e in tests)
print(json.dumps({"all_pass": all_pass, "count": len(tests)}))
"@
$ok4 = Assert-True "parse_output all cases" $r.all_pass $LOG_FILE

if ($ok4) { $pass++; Write-Log $LOG_FILE "  EX-04: PASS" }
else      { $fail++; Write-Log $LOG_FILE "  EX-04: FAIL" }

# -- EX-05: Error Paths ---------------------------------------------------------
Write-Log $LOG_FILE ""
Write-Log $LOG_FILE "=== EX-05: Error Paths ==="

$r = Invoke-Driver -LogFile $LOG_FILE -Label "not-installed" -Code @"
import sim.drivers.ansa.driver as drv
orig = drv._find_installation
drv._find_installation = lambda: None
try:
    d.run_file(Path(r'$FIXTURES\good_ansa_script.py'))
    print(json.dumps({"raised": False}))
except RuntimeError as e:
    print(json.dumps({"raised": True, "type": "RuntimeError"}))
finally:
    drv._find_installation = orig
"@
$ok5 = Assert-True "RuntimeError raised" $r.raised $LOG_FILE

if ($ok5) { $pass++; Write-Log $LOG_FILE "  EX-05: PASS" }
else      { $fail++; Write-Log $LOG_FILE "  EX-05: FAIL" }

# -- EX-06: Batch Execution (BLOCKED) -------------------------------------------
Write-Log $LOG_FILE ""
Write-Log $LOG_FILE "=== EX-06: Batch Execution ==="
Write-Log $LOG_FILE "  BLOCKED: ANSA license not configured (ANSA_SRV unresolved)"
Write-Log $LOG_FILE "  See known_issues.md for details"
$blocked++

# -- Summary -------------------------------------------------------------------
Write-Log $LOG_FILE ""
Write-Log $LOG_FILE "=========================================="
Write-Log $LOG_FILE "  SUMMARY"
Write-Log $LOG_FILE "    PASS:    $pass / 6"
Write-Log $LOG_FILE "    FAIL:    $fail / 6"
Write-Log $LOG_FILE "    BLOCKED: $blocked / 6"
Write-Log $LOG_FILE "=========================================="
Write-Log $LOG_FILE "  Logs: $LOG_DIR"
