# Transmission media

`skrf.media` defines analytic transmission lines that can generate
N-port networks (short, open, line, gamma_load, ...).

## Common media

```python
from skrf.media import (
    DefinedGammaZ0, Coaxial, CPW, RectangularWaveguide, Freespace,
)

# Generic — define propagation constant + characteristic impedance
gen = DefinedGammaZ0(freq, gamma=1j*freq.w/3e8, z0=50)

# Coaxial cable
coax = Coaxial(freq, Dint=2.6e-3, Dout=8.66e-3, sigma=1e7, epsilon_r=2.2)

# Co-planar waveguide
cpw = CPW(freq, w=1.0e-3, s=0.5e-3, ep_r=4.4, t=35e-6)

# Rectangular metal waveguide (TE10)
wg = RectangularWaveguide(freq, a=22.86e-3, b=10.16e-3)

# Free space (for antennas / radiated coupling)
fs = Freespace(freq)
```

## Generating standard loads from a medium

```python
short_ntwk = line.short()
open_ntwk  = line.open()
match_ntwk = line.match()                         # 50 Ω
delay      = line.delay_short(d=10, unit='mm')    # short with line length
load       = line.resistor(R=75)
```

## Generating 2-port elements

```python
seg     = line.line(d=10, unit='mm')              # uniform line segment
attn    = line.attenuator(s21_db=-3)              # ideal attenuator
shunt   = line.shunt_capacitor(C=1e-12)
series  = line.series_inductor(L=1e-9)
```

## Composing a circuit

```python
filter_ntwk = (
    line.line(5, 'mm') ** line.shunt_capacitor(C=2e-12) **
    line.line(5, 'mm') ** line.short()
)
```
