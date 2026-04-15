# Standard libraries

## Built-in cable / line types

```python
import pandapower as pp
net = pp.create_empty_network()

# Distribution cables (LV / MV)
'NAYY 4x50 SE'      # PVC, 50 mm² alu, 4-conductor
'NAYY 4x150 SE'     # 150 mm² alu
'NA2XS2Y 1x95 RM/25 12/20 kV'   # MV cross-linked PE
'NA2XS2Y 1x240 RM/25 12/20 kV'

# Overhead lines
'149-AL1/24-ST1A 110.0'   # 110 kV ACSR

# List all available
pp.available_std_types(net, 'line')
```

## Built-in transformer types

```python
'0.25 MVA 20/0.4 kV'     # distribution
'0.4 MVA 20/0.4 kV'
'0.63 MVA 20/0.4 kV'
'25 MVA 110/20 kV'       # MV/LV substation
'160 MVA 380/110 kV'     # transmission

pp.available_std_types(net, 'trafo')
pp.available_std_types(net, 'trafo3w')      # 3-winding
```

## IEEE benchmark networks

`pandapower.networks` contains canonical test cases:

```python
import pandapower.networks as pn
net = pn.case4gs()              # 4-bus Glover & Sarma
net = pn.case9()                # 9-bus
net = pn.case14()               # IEEE 14-bus
net = pn.case30()               # IEEE 30-bus
net = pn.case57()               # IEEE 57-bus
net = pn.case118()              # IEEE 118-bus
net = pn.case300()              # IEEE 300-bus

# CIGRE benchmark
net = pn.create_cigre_network_lv()
net = pn.create_cigre_network_mv(with_der='all')

# European LV / MV reference
net = pn.example_simple()
net = pn.simple_mv_open_ring_net()
```

These are excellent for sanity-checking driver behavior — known
results are published.
