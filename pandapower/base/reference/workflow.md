# pandapower workflow

```python
import pandapower as pp

# 1. Empty network
net = pp.create_empty_network()

# 2. Buses (specify nominal voltage)
b1 = pp.create_bus(net, vn_kv=20.0,  name='Slack')
b2 = pp.create_bus(net, vn_kv=20.0,  name='Load')
b3 = pp.create_bus(net, vn_kv=0.4,   name='LV')

# 3. Slack reference (mandatory for AC PF)
pp.create_ext_grid(net, b1, vm_pu=1.0)

# 4. Branches
pp.create_line(net, b1, b2, length_km=10, std_type='NAYY 4x150 SE')
pp.create_transformer(net, hv_bus=b2, lv_bus=b3, std_type='0.4 MVA 20/0.4 kV')

# 5. Loads / generators
pp.create_load(net, b3, p_mw=0.3, q_mvar=0.1)
pp.create_sgen(net, b2, p_mw=0.5, name='PV')   # static gen (PV / wind)

# 6. Run AC power flow
pp.runpp(net)

# 7. Read out
print(net.res_bus.vm_pu)      # voltages (p.u.)
print(net.res_line.loading_percent)
print(net.res_line.pl_mw, net.res_line.ql_mvar)   # losses
```

## Always emit JSON

```python
import json
print(json.dumps({
    "ok": True,
    "vm_min": float(net.res_bus.vm_pu.min()),
    "vm_max": float(net.res_bus.vm_pu.max()),
    "loss_mw": float(net.res_line.pl_mw.sum()),
}))
```
