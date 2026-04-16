# ICEM CFD E2E: Box.tin → tetra mesh → save unstructured domain.
#
# Uses the documented batch commands from the Programmer's Guide:
#   ic_load_tetin   (p9)  — load geometry
#   ic_run_tetra    (p143) — batch tetra mesher
#   ic_save_unstruct (discovered) — save domain file
#
# Vendor input: Box.tin from ICEM TestInputs/
# Runs via: sim run scripts/run.tcl --solver icem

set workdir [file dirname [info script]]/..
set tin_path "$workdir/inputs/Box.tin"
set out_uns  "$workdir/evidence/box_tetra.uns"

file mkdir "$workdir/evidence"

# 1. Load geometry
puts "Step 1: Loading tetin geometry..."
if {[catch {ic_load_tetin $tin_path} err]} {
    puts "{\"ok\": false, \"step\": \"load_tetin\", \"error\": \"$err\"}"
    exit 1
}
puts "  Geometry loaded."

# 2. Run batch tetra mesher (Programmer's Guide p143)
#    ic_run_tetra tetin uncut_dom args
puts "Step 2: Running tetra mesher..."
if {[catch {ic_run_tetra $tin_path $out_uns} err]} {
    puts "{\"ok\": false, \"step\": \"run_tetra\", \"error\": \"$err\"}"
    exit 1
}
puts "  Tetra meshing completed."

# 3. Check output
set out_exists [file exists $out_uns]
set out_size 0
if {$out_exists} {
    set out_size [file size $out_uns]
}

puts "{\"ok\": $out_exists, \"output\": \"$out_uns\", \"file_exists\": $out_exists, \"file_size_bytes\": $out_size}"
exit 0
