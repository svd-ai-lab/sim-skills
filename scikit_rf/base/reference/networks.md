# Network class

## Construction

```python
import skrf as rf

# From file
ntwk = rf.Network('foo.s2p')

# From numpy arrays
import numpy as np
freq = rf.Frequency(1, 10, 11, 'GHz')
S = np.zeros((11, 2, 2), dtype=complex)
ntwk = rf.Network(frequency=freq, s=S, z0=50, name='my_ntwk')
```

## Parameter conversions (all return ndarray of shape (n_freq, n_ports, n_ports))

| Attribute | Meaning |
|---|---|
| `ntwk.s` | S-parameters (default native) |
| `ntwk.z` | Z (impedance) parameters |
| `ntwk.y` | Y (admittance) parameters |
| `ntwk.t` | T (transfer scattering) — 2-port only |
| `ntwk.a` | ABCD parameters — 2-port only |
| `ntwk.s_db` | 20·log10(|S|) |
| `ntwk.s_deg` | angle(S) in degrees |
| `ntwk.s_rad` | angle(S) in radians |
| `ntwk.s_vswr` | (1+|S|)/(1-|S|) |

## Slicing in frequency

```python
sub = ntwk['1-5GHz']                # frequency string slice
sub = ntwk['2GHz']                  # nearest single point
```

## Math operators

```python
n3 = n1 ** n2                       # cascade (2-port)
n3 = n1 + n2                        # parallel
n3 = n1 // n2                       # series
inv = n1.inv                        # inverse 2-port
```

## Plotting (matplotlib backend)

```python
ntwk.plot_s_db()                    # |S| in dB vs freq
ntwk.plot_s_smith()                 # Smith chart
ntwk.plot_s_polar()
```
