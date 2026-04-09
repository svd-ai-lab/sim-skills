# PyBaMM skill index

You are connected to the **pybamm** driver in sim-cli. PyBaMM is a pure
Python battery simulation library — no separate solver binary, no JVM,
no GUI. The "solver version" is the `pybamm` package version itself.

The `/connect` response told you which active layers apply via
`active_sdk_layer`. The base layer is always relevant; the sdk layer
overlays on top of it.

## Always relevant — `base/`

- `base/reference/` — concepts: what a battery model is, what DFN/SPM/SPMe
  mean, parameter sets, observables
- `base/snippets/` — copy-pasteable starters: build a sim, run a charge
  cycle, plot voltage/current

## SDK-version-specific — `sdk/<your-active-sdk-layer>/`

Your `active_sdk_layer` is one of:

- `24` — PyBaMM 24.x line. Stable Battery_DFN / SPMe / SPM API.
- `25` — PyBaMM 25.x line. Latest tested.

Look in `sdk/<your-version>/` for:

- API differences from the previous major (method/kwarg renames)
- newly added models or parameter sets
- known regressions

## Lookup order

1. `base/` for the concepts and the shape of the workflow
2. `sdk/<active>/` for the exact API call to use today

A file in `sdk/` overrides anything in `base/` on the same topic — when
in doubt, prefer the more specific one.

## Solver layer

PyBaMM has no separate solver binary, so there is no `solver/` overlay.
`active_solver_layer` will always be `null` for this driver.
