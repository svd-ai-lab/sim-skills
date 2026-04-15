# pandapower 2.x Notes

## Provenance

- Source: PyPI `pandapower`
- Verified version: 2.11.1
- Pure Python + pandas + numpy/scipy + (optional) numba

## Capabilities verified

| Feature | Status | Notes |
|---------|--------|-------|
| `create_empty_network()` | Verified | |
| `create_bus(net, vn_kv)` | Verified | returns int index |
| `create_ext_grid(net, bus)` | Verified | slack reference |
| `create_line(net, b1, b2, length_km, std_type)` | Verified | std lib types |
| `create_load(net, bus, p_mw)` | Verified | |
| `runpp(net)` | Verified | converges in <10 iter for small nets |
| `net.res_bus.vm_pu` | Verified | pandas Series |

## 2-bus PF benchmark

20 kV slack — 10 km NAYY 4x150 SE — 0.5 MW load:
vm_pu(b2) = 0.998 (small drop)
losses = 1.4 kW (consistent with cable R, low load)

## Version detection

```bash
python3 -c "import pandapower; print(pandapower.__version__)"
```
returns `2.11.1`. Driver normalizes to `2.11`.

## Companion ecosystem

- `pandapower.networks` — IEEE / CIGRE benchmark cases (built-in)
- `pandapower.shortcircuit` — IEC 60909 short-circuit
- `pandapower.timeseries` — multi-step PF over time profiles
- `pandapipes` (separate package) — gas / district-heating networks
