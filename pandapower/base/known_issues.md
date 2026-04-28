# Known Issues — pandapower Driver

## ext_grid required for AC PF

**Status**: API
**Description**: AC power flow needs a slack bus. If no `ext_grid` AND
no `gen(slack=True)` exist, `runpp` raises. For islanded micro-grids
use a `gen` with `slack=True`.

## Numba speedup warning if not installed

**Status**: Cosmetic
**Description**: `Numba could not be installed... slow execution` is
just a warning. Either install numba (`pip install numba`) or pass
`runpp(net, numba=False)` to silence.

## net.res_* tables empty before runpp

**Status**: API design
**Description**: `net.res_bus` only has data after a successful
`pp.runpp(net)`. Don't access before.

## Convergence failure detection

**Status**: User responsibility
**Description**: If PF doesn't converge, `pp.runpp` raises (or with
`run_control=True`, sets `net.converged = False`). Check before reading
results.

## numpy bool / float in res_bus

**Status**: Common gotcha
**Description**: `net.res_bus.vm_pu[b]` returns numpy float; cast
with `float(...)` for `json.dumps`.

## Voltage mismatch silently breaks PF

**Status**: User error
**Description**: A line connecting two buses with different `vn_kv`
behaves incorrectly. Use a transformer between voltage levels.

## std_types must match the chosen voltage class

**Status**: Library design
**Description**: `'NAYY 4x150 SE'` is an LV cable (0.4 kV); using it
on a 20 kV line is technically allowed but gives nonsense impedances.
Use MV cable types (`'NA2XS2Y...'`) for MV.

## Element indices are int (or RangeIndex)

**Status**: Convention
**Description**: `b = pp.create_bus(...)` returns the integer index
into `net.bus`. Use this index when wiring branches and reading
results — NOT the bus name.
