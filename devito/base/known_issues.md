# Known Issues — Devito Driver

## C compiler required at runtime

**Status**: Hard dep
**Description**: Devito generates and JIT-compiles C kernels. Without
gcc / clang on PATH at apply-time, you get an opaque error from the
codegen layer. Set `DEVITO_ARCH=gcc` (or `clang`) to be explicit.

## TimeFunction memory layout is cyclic

**Status**: API design
**Description**: `TimeFunction(time_order=N)` allocates only N+1 time
slots, used cyclically. To save more history, allocate a separate
`Function` and copy at each step, or save into HDF5.

## CFL stability is your responsibility

**Status**: Math
**Description**: For diffusion: `dt ≤ dx² / (2*α)` (1D), tighter in
higher dim. For wave: `dt ≤ CFL * dx / v_max` with CFL ≈ 0.5 for
2nd-order, lower for higher orders. Devito does NOT auto-check.

## space_order vs accuracy

**Status**: Convention
**Description**: `space_order=2` → standard 3-point stencil, 2nd-order
accurate. `space_order=8` → 9-point stencil, 8th-order accurate but
4x as many flops per cell. Use 4-8 for wave problems.

## Codegen cache pollution

**Status**: Disk usage
**Description**: First run of every Operator caches compiled `.so` in
`~/.devito` or `$DEVITO_AUTOTUNING`. Cache can grow to GBs over time.
Clear via `rm -rf ~/.devito/jitcache`.

## numpy array assignment vs slice

**Status**: Convention
**Description**: `u.data[0] = arr` works (assigns to time-step 0).
But `u.data = arr` raises (can't replace the whole TimeFunction storage).

## `solve()` requires the equation to be linear in target

**Status**: API design
**Description**: `solve(Eq(u.dt, RHS), u.forward)` works because the
LHS is linear in `u.forward` after time discretization. For nonlinear
PDEs in `u.forward`, build the explicit update yourself or iterate.
