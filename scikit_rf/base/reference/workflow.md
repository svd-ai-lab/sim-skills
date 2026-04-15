# scikit-rf workflow

```python
import skrf as rf
import numpy as np

# 1. Frequency band
freq = rf.Frequency(start=1, stop=10, npoints=101, unit='GHz')

# 2. Transmission media (50 Ω line in this example)
line = rf.media.DefinedGammaZ0(freq, z0=50.0)

# 3. Build networks
short    = line.short()
open_    = line.open()
match_   = line.match()
delay25  = line.delay_load(0.5, 25, 'mm')          # delay-load
seg      = line.line(d=10, unit='mm')              # transmission segment

# 4. Connect / cascade (port indexing is 1-based)
two_port = line.line(d=10, unit='mm')              # 2-port line
combined = rf.connect(two_port, 1, line.short(), 0)  # short on port 1

# 5. Read S-parameters
S = combined.s                                      # shape (n_freq, 2, 2)
S11 = S[:, 0, 0]                                    # complex
S11_db = 20 * np.log10(np.abs(S11))

# 6. Touchstone I/O
ntwk = rf.Network('measured.s2p')
ntwk.write_touchstone('out.s2p')
```

## Always emit JSON

```python
import json
print(json.dumps({
    "ok": True,
    "S11_at_5GHz_re": float(S11[5].real),
    "S11_at_5GHz_im": float(S11[5].imag),
    "S11_at_5GHz_dB": float(20 * np.log10(abs(S11[5]))),
}))
```
