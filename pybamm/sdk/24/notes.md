# PyBaMM 24.x notes

24.x is the long-stable line. The Battery_DFN / SPMe / SPM model APIs
match the patterns shown in `base/`. No SDK-version-specific overrides
are required for the snippets in `base/snippets/`.

## Known stable patterns

- `pybamm.Simulation(model, parameter_values=...)` — direct kwarg
- `solution["Voltage [V]"].entries` — numpy array

## Notes

This file exists so the layer is non-empty and `verify_skills_layout`
passes. As 24.x and 25.x diverge, real overrides will land here.
