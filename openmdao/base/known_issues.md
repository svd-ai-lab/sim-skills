# Known Issues — OpenMDAO Driver

## Cyclic groups need a NL solver

**Status**: API design
**Description**: A group with a feedback loop (D1 → D2 → D1) requires
`group.nonlinear_solver = om.NonlinearBlockGS()` (or NewtonSolver).
Without it, the residual loop is open and `run_model()` errors.

## `setup()` must be called before `run_*`

**Status**: API design
**Description**: `Problem.setup()` builds the variable graph and
allocates arrays. Skipping it raises `RuntimeError: Problem
has not been set up`.

## Setting inputs before vs after setup

**Status**: API quirk
**Description**: Use `model.set_input_defaults('x', val)` BEFORE
`setup()`. Use `prob['x'] = val` AFTER `setup()`. Doing it in
the wrong order silently uses defaults.

## NumPy array shape must match `add_input(val=...)`

**Status**: User error
**Description**: If `add_input('z', val=np.zeros(2))` declares shape
(2,), then assigning a scalar later raises shape mismatch. Use
`np.array([...])` consistently.

## Driver `iter_count` reset between runs

**Status**: Convention
**Description**: `prob.driver.iter_count` is the count for the last
`run_driver()` call. Multiple sequential runs do not accumulate.

## Verbose output

**Status**: Cosmetic
**Description**: Solver/driver iteration prints can be silenced via
`solver.options['iprint'] = 0` and `driver.options['disp'] = False`.

## Python 3.7 deprecation warning

**Status**: Watch
**Description**: 3.30.x prints `OMDeprecationWarning` for Python 3.7
support sunset. Driver runs fine; upgrade Python at next opportunity.

## Recorder output format

**Status**: Convention
**Description**: `SqliteRecorder` writes a `.sql` (SQLite). Read with
`om.CaseReader('cases.sql')`. Not human-readable; use `case.get_design_vars()`
etc. for inspection.
