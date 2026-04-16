# ICEM CFD smoke test — verify batch mode launches + Tcl executes.
#
# Runs via: sim run base/snippets/01_smoke_test.tcl --solver icem
#
# Acceptance: exit_code == 0, JSON has ok=true

puts "{\"ok\": true, \"tcl_version\": \"[info patchlevel]\", \"batch\": \"icem\"}"
exit 0
