# Calibration

scikit-rf provides VNA calibration algorithms to remove systematic errors.

## One-port calibration (3-term: short, open, match)

```python
import skrf as rf
from skrf.calibration import OnePort

# Ideal standards (or measured ones)
ideal_short = rf.media.DefinedGammaZ0(freq, z0=50).short()
ideal_open  = ...short().inv  # placeholder
ideal_match = rf.media.DefinedGammaZ0(freq, z0=50).match()

# Measured raw S11 of the same standards
meas_short  = rf.Network('cal_short.s1p')
meas_open   = rf.Network('cal_open.s1p')
meas_match  = rf.Network('cal_match.s1p')

cal = OnePort(
    ideals=[ideal_short, ideal_open, ideal_match],
    measured=[meas_short, meas_open, meas_match],
)
cal.run()

# Apply to DUT
dut_meas = rf.Network('dut.s1p')
dut_cal  = cal.apply_cal(dut_meas)
```

## SOLT (12-term, 2-port)

```python
from skrf.calibration import SOLT
solt = SOLT(
    ideals=[ideal_thru, ideal_open, ideal_short, ideal_match],
    measured=[meas_thru, meas_open, meas_short, meas_match],
)
solt.run()
dut_cal_2p = solt.apply_cal(rf.Network('dut.s2p'))
```

## TRL (multiline, 2-port)

```python
from skrf.calibration import TRL
trl = TRL(
    measured=[meas_thru, meas_reflect, meas_line],
    Grefls=[-1],
    line_lengths=[10e-3],
)
trl.run()
```

## Caveats

- Standards must use the **same frequency grid** as the DUT measurement.
- TRL needs the line standard's electrical length to be ~λ/4 at the
  band center; multi-line TRL (mTRL) gives broadband.
- `cal.apply_cal()` returns a NEW Network; the original is untouched.
