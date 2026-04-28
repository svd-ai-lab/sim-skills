# Known Issues — OpenSeesPy Driver

## `Process 0 Terminating` on stderr

**Status**: Cosmetic
**Description**: OpenSees C++ core writes this string to stderr on every
interpreter exit, success or failure. Do **not** treat stderr non-empty
as a failure signal. Use `ops.analyze()` return code (0 = success) and
your acceptance JSON instead.

## Global state — wipe() between runs

**Status**: Convention
**Description**: All `model`, `node`, `element`, etc. live on a process-global
table. Successive scripts in the same Python process accumulate state.
Begin every script with `ops.wipe()`.

## ndf mismatch is silent

**Status**: API design
**Description**: If `ndf=3` was set but `fix` is called with 2 args,
OpenSeesPy raises immediately. But if `load` is called with too many
args, the extras are silently dropped. Always count args == ndf for
load / fix / mass calls.

## Static analysis requires the FULL chain

**Status**: API design
**Description**: All six commands (`system`, `numberer`, `constraints`,
`integrator`, `algorithm`, `analysis`) must be set before `analyze()`.
Skipping any → "analysis object not constructed" (cryptic).

## eigen requires Static analysis context

**Status**: API quirk
**Description**: For modal/eigenvalue analyses, you still need to set
up a Static analysis chain (without calling `analyze()`), then call
`ops.eigen(N)`. Without the chain, `eigen` errors out.

## Version detection on Python 3.7

**Status**: Standard library gap
**Description**: `importlib.metadata` is 3.8+. The driver falls back to
`importlib_metadata` and then `pkg_resources`. If both are missing on a
3.7 host, `connect()` will report `not_installed` even when the wheel
is importable.

## No native MPI

**Status**: Limitation
**Description**: The pip wheel is serial only. Parallel OpenSees
(`OpenSeesMP`) requires a separate source build with PETSc + MPI.
Out of scope for this driver.
