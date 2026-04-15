---
name: cantera-sim
description: Use when driving Cantera (open-source thermodynamics, chemical kinetics, transport library from LBNL/Caltech) via Python scripts — equilibrium, ideal-gas / surface kinetics, premixed/diffusion flames, batch / PFR / well-stirred reactors — through sim runtime one-shot execution.
---

# cantera-sim

You are connected to **Cantera** via sim-cli.

Cantera is the canonical open-source library for combustion and chemistry
modeling. Pip-installable (`pip install cantera`); ships compiled C++
kernel + Python bindings + standard mechanisms (`gri30.yaml`,
`h2o2.yaml`, `air.yaml`, ...).

Scripts are plain `.py`:

```python
import cantera as ct
gas = ct.Solution('gri30.yaml')
gas.TPX = 300, ct.one_atm, 'CH4:1, O2:2, N2:7.52'
gas.equilibrate('HP')
print(gas.T, gas['CO2'].X)
```

Same subprocess driver mode as PyBaMM / PyMFEM / SfePy.

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/workflow.md` | Solution → state → process (equilibrate / advance / solve). |
| `base/reference/states.md` | TPX / TPY / HP / SV / UV setters; `set_equivalence_ratio`. |
| `base/reference/reactors.md` | Reactor / ReactorNet / FlowReactor / WSR. |
| `base/reference/flames.md` | FreeFlame, BurnerFlame, CounterflowDiffusionFlame. |
| `base/snippets/01_adiabatic_flame.py` | Verified adiabatic flame T E2E. |
| `base/known_issues.md` | YAML mechanism format, stale 2.5 vs 3.x API differences. |

## sdk/2/ — Cantera 2.x

- `sdk/2/notes.md` — version-specific surface notes.

---

## Hard constraints

1. **`Solution(...)` requires a YAML mechanism file.** Built-in:
   `gri30.yaml` (natural gas), `h2o2.yaml` (hydrogen), `air.yaml`,
   `airNASA9.yaml`. Custom files are loaded by absolute path.
2. **Property setters are tuples, not method calls**:
   ```
   gas.TPX = 300, ct.one_atm, 'CH4:1, O2:2'    # T, P, mole fractions
   gas.TPY = 300, ct.one_atm, 'CH4:0.055, ...'  # mass fractions
   gas.HP  = h, ct.one_atm                       # enthalpy + pressure
   ```
3. **`equilibrate(mode)` modes** — pick the conserved pair:
   - `'TP'` — fixed T, P
   - `'HP'` — adiabatic, fixed P (combustion)
   - `'SP'` — isentropic
   - `'UV'` — constant volume / energy
4. **Reactor networks need `ReactorNet`**. A bare `IdealGasReactor`
   has no time integrator; wrap in `ReactorNet([r1, r2, ...])` then
   call `net.advance(t)` or `net.step()`.
5. **Acceptance != "ran without error"**. Validate against textbook
   values (CH4/air adiabatic ~2225 K, H2/O2 ~3000 K, ignition delays
   from Shock Tube database, flame speeds from PIV).
6. **Print results as JSON on the last stdout line.**

---

## Required protocol

1. Gather inputs:
   - **Category A:** mechanism, initial state (T, P, composition),
     process (equilibrate mode / reactor type / flame configuration),
     acceptance criterion.
   - **Category B:** solver tolerances, max steps, transport model.
2. `sim check cantera` — confirms wheel + mechanisms are importable.
3. Write `.py` per `base/reference/workflow.md`.
4. `sim lint script.py`.
5. `sim run script.py --solver cantera`.
6. Validate JSON against the acceptance criterion.
