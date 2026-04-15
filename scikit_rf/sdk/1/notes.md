# scikit-rf 1.x Notes

## Provenance

- Source: PyPI `scikit-rf`
- Verified version: 1.1.0
- Pure Python + NumPy/SciPy/matplotlib

## Capabilities verified

| Feature | Status | Notes |
|---------|--------|-------|
| `rf.Frequency(start, stop, n, unit)` | Verified | GHz / MHz / Hz |
| `rf.media.DefinedGammaZ0(freq, z0=50)` | Verified | 50 Ω line |
| `line.short()`, `.open()`, `.match()` | Verified | exact -1 / +1 / 0 |
| `ntwk.s` access | Verified | (n_freq, n_p, n_p) complex |

## Standard-loads benchmark

50-Ω line, 1-10 GHz, 11 points:
S11(short) = -1.000 + 0.000j (exact)
S11(open)  = +1.000 + 0.000j (exact)
S11(match) =  0.000 + 0.000j (exact)

## Version detection

```bash
python3 -c "import skrf; print(skrf.__version__)"
```
returns `1.1.0`. Driver normalizes to `1.1`.

## Companion ecosystem

- `skrf.calibration` — SOLT / TRL / OnePort cal algorithms (built-in)
- `skrf.io` — Touchstone, MDIF, CITI file I/O (built-in)
- `pyvna` (separate package) — VNA control via PyVISA
