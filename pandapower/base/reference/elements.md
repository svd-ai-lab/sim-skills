# Network elements

| Element | Creator | Required args |
|---|---|---|
| Bus | `create_bus(net, vn_kv, ...)` | nominal voltage |
| Line | `create_line(net, b1, b2, length_km, std_type)` | length + cable spec |
| Line (custom) | `create_line_from_parameters(net, b1, b2, length_km, r_ohm_per_km, x_ohm_per_km, c_nf_per_km, max_i_ka)` | impedance per km |
| Transformer | `create_transformer(net, hv_bus, lv_bus, std_type)` | trafo type from library |
| Trafo (custom) | `create_transformer_from_parameters(...)` | sn_mva, vn_hv_kv, vn_lv_kv, vk_percent, vkr_percent, ... |
| External grid | `create_ext_grid(net, bus, vm_pu)` | slack reference |
| Load | `create_load(net, bus, p_mw, q_mvar)` | active+reactive power |
| Static gen | `create_sgen(net, bus, p_mw, q_mvar)` | PV/wind/storage inverter |
| Generator | `create_gen(net, bus, p_mw, vm_pu, slack=False)` | PV bus or slack |
| Storage | `create_storage(net, bus, p_mw, max_e_mwh, ...)` | battery |
| Switch | `create_switch(net, bus, element, et='l')` | bus-line / bus-bus switch |

## Tables (after creation, before runpp)

```python
print(net.bus)        # bus table (input data)
print(net.line)
print(net.load)
print(net.ext_grid)
```

## Result tables (after runpp)

```python
print(net.res_bus)         # vm_pu, va_degree, p_mw, q_mvar
print(net.res_line)        # p_from_mw, p_to_mw, pl_mw, loading_percent, ...
print(net.res_trafo)       # similar
print(net.res_load)
print(net.res_gen, net.res_sgen)
```

## Built-in standard libraries

```python
pp.available_std_types(net, element='line')           # list of cable types
pp.available_std_types(net, element='trafo')
pp.load_std_type(net, 'NAYY 4x150 SE', element='line')
```
