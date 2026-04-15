# Known Issues — pymoo Driver

## Python 3.7 only supports pymoo 0.6.0 or earlier

**Status**: Compatibility
**Description**: `pymoo>=0.6.1` imports `typing.Literal` which is 3.8+.
On Python 3.7 hosts, pin `pip install 'pymoo<=0.6.0'`. Newer Python is
fine across the board.

## `res.F` shape varies by problem type

**Status**: API design
**Description**:
- Multi-obj: `res.F` is `(n_pareto, n_obj)`
- Single-obj: `res.F` is `(1, 1)` — still 2D, take `res.F[0, 0]`
- No feasible solution found: `res.F` may be `None`. Check first.

## Seed not propagated when omitted

**Status**: Reproducibility
**Description**: Without `seed=...`, runs are non-deterministic. Always
seed for benchmarks and CI tests.

## Vectorized vs ElementwiseProblem perf gap

**Status**: Performance
**Description**: `ElementwiseProblem` evaluates one solution per call;
`Problem` evaluates the whole population at once. For analytic objectives,
the vectorized form is 10-100x faster.

## Constraint sign convention: G <= 0

**Status**: Convention
**Description**: pymoo enforces `G <= 0` and `H == 0`. To impose
`g(x) >= a`, transform to `out['G'] = a - g(x)`.

## `verbose=True` floods stdout

**Status**: Cosmetic
**Description**: For `sim` runs, set `verbose=False` and emit a JSON
summary at the end. Otherwise the parser ignores the iteration table
but the run history balloons.
