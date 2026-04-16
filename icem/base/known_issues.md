# ICEM CFD known issues

## KI-001 — med_batch.exe hangs without `exit 0`

**Symptom**: Script finishes but process never terminates.

**Fix**: Always end Tcl scripts with `exit 0`.

## KI-002 — Zero elements from open geometry

**Symptom**: `ic_uns_run_mesh` completes without error but produces
0 elements in the domain.

**Cause**: Input geometry has open surfaces — tetra meshing requires
a watertight volume.

**Fix**: Verify geometry is closed before meshing. Use
`ic_geo_check_surface_closure` if available.

## KI-003 — Output interface prompts in batch mode

**Symptom**: `med_batch.exe` hangs at an export step (e.g.
`fluent_write_input`).

**Cause**: The output interface `.tcl` module uses `tk_dialog` or
similar interactive prompts.

**Fix**: Set `ic_batch_mode 1` at the top of the script. Specify all
file paths explicitly rather than relying on interactive selection.

## KI-004 — Tcl version varies (documented 8.3.3, actual 8.4.11)

**Symptom**: ICEM docs reference Tcl 8.3.3 but the actual embedded
interpreter reports `info patchlevel` = `8.4.11` (at least on 24.1).

**Impact**: 8.4.11 supports `{*}` expansion and a few features missing
in 8.3.3, but still doesn't have `dict` or `lmap`.

**Fix**: Target Tcl 8.4 as the minimum. Avoid `dict` / `lmap`.

## KI-008 — `ic_batch_mode` takes no arguments

**Symptom**: `ic_batch_mode 1` fails with `wrong # args: should be
"ic_batch_mode"`.

**Fix**: Call `ic_batch_mode` without arguments (it's a simple toggle,
not a setter). Discovered during first E2E smoke test.

## KI-005 — Backslash in Windows paths

**Symptom**: `ic_load_tetin "C:\work\model.tin"` fails with
`invalid command name "C:workmodel.tin"`.

**Cause**: Tcl interprets `\w` and `\m` as escape sequences.

**Fix**: Use forward slashes: `ic_load_tetin "C:/work/model.tin"`.

## KI-006 — `ic_*` commands don't raise on error

**Symptom**: A command fails silently (prints to stderr) but the
script continues as if nothing happened.

**Fix**: Wrap in `catch`:
```tcl
if {[catch {ic_uns_run_mesh} err]} {
    puts "ERROR: $err"
    exit 1
}
```

## KI-007 — License checkout delay

**Symptom**: `med_batch.exe` takes 10-20s before executing the first
`ic_*` command.

**Cause**: ICEM acquires its own license feature from the Ansys license
server on startup.

**Mitigation**: Ensure `ANSYSLMD_LICENSE_FILE` is set and the license
server is on the same LAN.
