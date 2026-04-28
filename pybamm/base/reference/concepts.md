# PyBaMM concepts

PyBaMM = "Python Battery Mathematical Modelling". A library for
continuum-scale battery models, mostly used for Li-ion cells.

## Core objects

- **Model** — the physics. `pybamm.lithium_ion.SPM`, `SPMe`, `DFN`.
  Single-Particle Model is fastest; DFN (Doyle-Fuller-Newman) is the
  most detailed.
- **ParameterValues** — the numbers. Pick from a built-in set
  (`pybamm.ParameterValues("Chen2020")`) or build one from scratch.
- **Experiment** — the protocol. A list of strings like
  `"Discharge at 1C until 3.3V"`, `"Rest for 30 minutes"`.
- **Simulation** — ties model + parameters + experiment together.
  Call `.solve()` and inspect `.solution`.

## Typical workflow

1. Pick a model
2. Pick a parameter set
3. Build a Simulation
4. (Optional) attach an Experiment
5. Solve
6. Read variables out of `solution["Variable name"].entries`

## Common variables

- `"Voltage [V]"` — terminal voltage
- `"Current [A]"`
- `"Time [s]"`
- `"Discharge capacity [A.h]"`
- `"X-averaged negative particle concentration"` etc.

Variable names are case- and unit-sensitive. The full list is in the
solution: `solution.all_models[0].variable_names()`.
