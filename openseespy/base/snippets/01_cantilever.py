"""Step 1: Cantilever beam tip deflection (verified E2E).

Geometry: 2D cantilever, L=1.0 m, P=-1000 N at tip.
Section: A=1e-2 m^2, I=1e-6 m^4, E=2e11 Pa.

Analytical: delta = P*L^3/(3*E*I) = -1.6667e-3 m
Observed:   -1.6667e-3 m (rel error 1.3e-12) on 10 elasticBeamColumn elems.

Run: sim run 01_cantilever.py --solver openseespy
"""
import json
import openseespy.opensees as ops


def main():
    L, P, E, A, I, n = 1.0, -1000.0, 2.0e11, 1.0e-2, 1.0e-6, 10

    ops.wipe()
    ops.model('basic', '-ndm', 2, '-ndf', 3)

    for i in range(n + 1):
        ops.node(i + 1, i * L / n, 0.0)
    ops.fix(1, 1, 1, 1)

    ops.geomTransf('Linear', 1)
    for i in range(n):
        ops.element('elasticBeamColumn', i + 1, i + 1, i + 2, A, E, I, 1)

    ops.timeSeries('Linear', 1)
    ops.pattern('Plain', 1, 1)
    ops.load(n + 1, 0.0, P, 0.0)

    ops.system('BandSPD'); ops.numberer('RCM'); ops.constraints('Plain')
    ops.integrator('LoadControl', 1.0); ops.algorithm('Linear')
    ops.analysis('Static')
    status = ops.analyze(1)

    tip = ops.nodeDisp(n + 1, 2)
    analytical = P * L ** 3 / (3.0 * E * I)
    print(json.dumps({
        "ok": status == 0 and abs(tip - analytical) / abs(analytical) < 0.01,
        "tip_disp_m": tip,
        "analytical_m": analytical,
        "rel_error": abs(tip - analytical) / abs(analytical),
    }))


if __name__ == "__main__":
    main()
