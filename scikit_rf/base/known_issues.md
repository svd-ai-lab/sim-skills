# Known Issues — scikit-rf Driver

## Touchstone format auto-detect by extension

**Status**: Convention
**Description**: `.s1p` = 1-port, `.s2p` = 2-port, `.s3p` = 3-port, etc.
The number must match the header. `.snp` (generic) requires `n_ports`
to be parsed from header.

## Frequency grid mismatch

**Status**: User error
**Description**: Operations like `**` (cascade) require both networks
to share the same frequency grid. `n1.interpolate(n2.frequency)` to
re-grid first.

## S-parameter indexing is 0-based, port labels are 1-based

**Status**: API design
**Description**:
- `ntwk.s[:, 0, 0]` is S11 (zero-based slicing).
- `rf.connect(n1, 1, n2, 0)` connects n1's port-1 (port label) to
  n2's port-0 (port label). Easy off-by-one trap.

## Complex S-parameters not JSON-serializable

**Status**: Common gotcha
**Description**: `complex` doesn't serialize via `json`. Convert to
`[float(z.real), float(z.imag)]` or use magnitude/phase.

## Plot helpers require matplotlib

**Status**: Soft dep
**Description**: `ntwk.plot_s_db()` etc. need matplotlib (auto-pulled
by pip install). For headless runs, `matplotlib.use('Agg')` first.

## Network port impedance defaults to 50 Ω

**Status**: Convention
**Description**: All `media.*().short()` etc. produce networks with
`z0=50` by default. Renormalize via `ntwk.renormalize(75)` if you
need a different reference impedance.

## Calibration standards must be re-generated for each freq grid

**Status**: API design
**Description**: `OnePort` / `SOLT` ideals tied to a specific frequency
grid. Re-build the ideal `media.short()` etc. on the DUT's
`Frequency` before constructing the cal.
