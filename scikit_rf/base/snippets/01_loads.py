"""Step 1: Standard loads on a 50-Ω line (verified E2E).

S11 expectations:
- Short:  -1 + 0j
- Open:   +1 + 0j
- Match:   0 + 0j

Observed: matches to machine precision.

Run: sim run 01_loads.py --solver scikit_rf
"""
import json
import skrf as rf


def main():
    freq = rf.Frequency(1, 10, 11, 'GHz')
    line = rf.media.DefinedGammaZ0(freq, z0=50.0)
    s = line.short().s[5, 0, 0]
    o = line.open().s[5, 0, 0]
    m = line.match().s[5, 0, 0]
    print(json.dumps({
        "ok": (abs(s + 1) < 1e-12 and abs(o - 1) < 1e-12 and abs(m) < 1e-12),
        "S11_short": [float(s.real), float(s.imag)],
        "S11_open":  [float(o.real), float(o.imag)],
        "S11_match": [float(m.real), float(m.imag)],
    }))


if __name__ == "__main__":
    main()
