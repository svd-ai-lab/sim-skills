#!/bin/bash
# MAPDL 2D I-beam via sim session mode (Phase 2).
# Drives sim connect / exec / inspect / disconnect end-to-end,
# capturing every call into a transcript JSON.
set -e

SIM=E:/simcli/sim-cli/.venv/Scripts/sim.exe
HOST=127.0.0.1
EV=E:/simcli/sim-skills/mapdl/base/workflows/mapdl_beam_session/evidence
mkdir -p "$EV"

TRANSCRIPT="$EV/transcript.json"
echo '[' > "$TRANSCRIPT"
FIRST=1

record() {
    local label="$1"; shift
    local cmd="$SIM --host $HOST $*"
    echo "===== $label =====" >&2
    local out
    out="$("$SIM" --host "$HOST" "$@" 2>&1)"
    echo "$out" >&2
    if [ $FIRST -eq 0 ]; then echo ',' >> "$TRANSCRIPT"; fi
    FIRST=0
    jq -n --arg step "$label" --arg cmd "$cmd" --arg out "$out" \
        '{step: $step, command: $cmd, response: $out, ts: now|todate}' \
        >> "$TRANSCRIPT"
}

record ps-initial ps
record inspect-session inspect session.summary

STEP1='mapdl.prep7()
mapdl.et(1, "BEAM188")
mapdl.keyopt(1, 4, 1)
mapdl.mp("EX", 1, 2e7)
mapdl.mp("PRXY", 1, 0.27)
mapdl.sectype(1, "BEAM", "I", "ISection", 3)
mapdl.secoffset("CENT")
mapdl.secdata(15, 15, 29, 2, 2, 1)
_result = {"step": "prep_setup", "ok": True}'
record exec-1-prep exec --label prep_setup "$STEP1"

STEP2='mapdl.n(1, 0, 0, 0); mapdl.n(12, 110, 0, 0); mapdl.n(23, 220, 0, 0)
mapdl.fill(1, 12, 10); mapdl.fill(12, 23, 10)
for nn in mapdl.mesh.nnum[:-1]:
    mapdl.e(int(nn), int(nn) + 1)
_result = {"nodes": int(len(mapdl.mesh.nnum)),
           "elems": int(len(mapdl.mesh.enum))}'
record exec-2-mesh exec --label build_mesh "$STEP2"

record inspect-mesh inspect mesh.summary

STEP3='mapdl.finish(); mapdl.slashsolu()
for c in ("UX","UY","ROTX","ROTZ"):
    mapdl.d("all", c)
mapdl.d(1, "UZ"); mapdl.d(23, "UZ")
mapdl.f(12, "FZ", -22840.0)
mapdl.antype("STATIC")
mapdl.solve()
mapdl.finish()
_result = {"solved": True}'
record exec-3-solve exec --label solve "$STEP3"

record inspect-files-after-solve inspect workdir.files

PNG="$EV/session_mapdl_beam_uz.png"
STEP4="import numpy as np
mapdl.post1(); mapdl.set(1, 1)
uz = mapdl.post_processing.nodal_displacement('Z')
mapdl.post_processing.plot_nodal_displacement(
    'Z',
    savefig=r'$PNG',
    off_screen=True,
    window_size=(1200, 700),
    cmap='viridis',
    show_edges=True,
)
_result = {'min_uz_cm': float(uz.min()),
           'max_abs_uz_cm': float(np.max(np.abs(uz))),
           'png': r'$PNG'}"
record exec-4-post exec --label post "$STEP4"

record inspect-last-result inspect last.result

record disconnect disconnect

echo ']' >> "$TRANSCRIPT"

echo "Transcript: $TRANSCRIPT"
echo "PNG:        $PNG"
