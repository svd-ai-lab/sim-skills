---
name: pandapower-sim
description: Use when driving pandapower (Python power-system analysis library combining pandas data tables with PYPOWER-style solvers, from Fraunhofer IEE) via Python scripts — load flow, optimal power flow (OPF), short-circuit, time-series, contingency analysis on transmission / distribution networks — through sim runtime one-shot execution.
---

# pandapower-sim

You are connected to **pandapower** via sim-cli.

pandapower (Thurner et al., IEEE Trans. Power Systems 2018) is the
standard Python library for power-system analysis. Pure Python +
pandas + numpy/scipy (with optional Numba for speedup). Pip-installable
(`pip install pandapower`).

Scripts are plain `.py`:

```python
import pandapower as pp
net = pp.create_empty_network()
b1 = pp.create_bus(net, vn_kv=20.0); b2 = pp.create_bus(net, vn_kv=20.0)
pp.create_ext_grid(net, b1)
pp.create_line(net, b1, b2, length_km=10, std_type='NAYY 4x150 SE')
pp.create_load(net, b2, p_mw=0.5)
pp.runpp(net)
print(net.res_bus.vm_pu)            # bus voltage magnitudes (p.u.)
```

Same subprocess driver mode as PyBaMM / Cantera.

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/workflow.md` | Empty net → buses → branches → injections → run. |
| `base/reference/elements.md` | Bus / Line / Trafo / Load / Gen / SGen / ExtGrid / Storage / Switch. |
| `base/reference/solvers.md` | runpp (PF), runopp (OPF), runsc (short-circuit), runts (time-series). |
| `base/reference/standard_libs.md` | Built-in line types, transformer types, IEEE benchmark networks. |
| `base/snippets/01_pf.py` | Verified 2-bus power flow E2E. |
| `base/known_issues.md` | numpy bool serialization, AC vs DC PF, slack bus required. |

## sdk/2/ — pandapower 2.x

- `sdk/2/notes.md` — version-specific surface notes.

---

## Hard constraints

1. **Every network needs an `ext_grid`** (slack bus) for AC power flow,
   else `runpp` raises. For islanded systems use a `gen` with
   `slack=True`.
2. **Bus voltages set by `vn_kv`** — must match the line / transformer
   ratings on each side. Mismatched voltages silently cause
   convergence failures.
3. **Default `runpp` is AC Newton-Raphson**. For approximate / DC use
   `runpp(net, algorithm='dc')`. For three-phase: `runpp_3ph`.
4. **Acceptance != "ran without error"**. Always check that PF
   converged and bus voltages are within plausible bounds (typically
   0.95-1.05 p.u.) and line loadings < 100%.
5. **Result tables live on `net.res_*`** AFTER running. Empty before.
6. **Print results as JSON on the last stdout line.** Cast pandas
   floats: `float(net.res_bus.vm_pu[b])`.

---

## Required protocol

1. Gather inputs:
   - **Category A:** network topology (bus / line / trafo data),
     load and generation profiles, slack reference, acceptance.
   - **Category B:** PF algorithm, tolerance, max iterations.
2. `sim check pandapower`.
3. Write `.py` per `base/reference/workflow.md`.
4. `sim lint script.py`.
5. `sim run script.py --solver pandapower`.
6. Validate JSON.
