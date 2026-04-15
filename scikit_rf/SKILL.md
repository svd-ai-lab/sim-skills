---
name: scikit-rf-sim
description: Use when driving scikit-rf (Python RF / microwave network analysis library) via Python scripts — Touchstone (.s2p / .snp) I/O, S-parameter network manipulation, transmission-line and ABCD-matrix media, calibration (SOLT / TRL), time-gating, plotting on Smith chart — through sim runtime one-shot execution.
---

# scikit-rf-sim

You are connected to **scikit-rf** via sim-cli.

scikit-rf (Arsenovic et al.) is the standard Python library for RF /
microwave engineering: S-parameter network algebra, Touchstone I/O,
transmission line theory, calibration, time-gating, statistical
analysis. Pure Python + NumPy/SciPy/matplotlib. Pip-installable
(`pip install scikit-rf`); imported as `import skrf as rf`.

Scripts are plain `.py`:

```python
import skrf as rf
ntwk = rf.Network('measured.s2p')             # 2-port S-parameters
print(ntwk.s.shape, ntwk.f.shape)             # (n_freq, 2, 2), (n_freq,)
ntwk_db = 20 * np.log10(np.abs(ntwk.s))
```

Same subprocess driver mode as PyBaMM / Cantera / CoolProp.

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/workflow.md` | Frequency → media → Network → cascade → analyze. |
| `base/reference/networks.md` | Network class, S/Z/Y/T/ABCD conversions, slicing. |
| `base/reference/media.md` | DefinedGammaZ0, CPW, Coaxial, RectangularWaveguide. |
| `base/reference/calibration.md` | OnePort, SOLT, TRL calibration setups. |
| `base/snippets/01_loads.py` | Verified short / open / match E2E. |
| `base/known_issues.md` | Touchstone format quirks, indexing convention, complex S. |

## sdk/1/ — scikit-rf 1.x

- `sdk/1/notes.md` — version-specific surface notes.

---

## Hard constraints

1. **Frequency in Hz internally** (or use `rf.Frequency(start, stop, n, unit)`
   to construct from GHz/MHz). Plot-time conversions handled separately.
2. **S-parameters are complex arrays** of shape `(n_freq, n_ports, n_ports)`.
   Don't mix `.s_db` (dB magnitude) with raw `.s` (complex).
3. **Network port numbering is 0-based in indexing** (`ntwk.s[:, 0, 0]` is S11)
   but **1-based in port labels** for cascade/connect.
4. **Acceptance != "ran without error"**. Validate against textbook
   loads (S11 short = -1, open = +1, match = 0) or a measured Touchstone
   file from a vetted source.
5. **Print results as JSON on the last stdout line.** Cast complex via
   `[float(z.real), float(z.imag)]`.

---

## Required protocol

1. Gather inputs:
   - **Category A:** frequency band, media (CPW / coax / waveguide),
     network topology, acceptance criterion.
   - **Category B:** number of frequency points, plotting / output format.
2. `sim check scikit_rf`.
3. Write `.py` per `base/reference/workflow.md`.
4. `sim lint script.py`.
5. `sim run script.py --solver scikit_rf`.
6. Validate JSON.
