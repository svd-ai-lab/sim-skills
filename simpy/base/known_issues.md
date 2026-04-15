# Known Issues — SimPy Driver

## Generator vs coroutine

**Status**: API design
**Description**: SimPy uses `yield` (generators), NOT `await` (coroutines).
Mixing `async def` + `await env.timeout(...)` will not work.

## env.now is float

**Status**: Convention
**Description**: All times are floats. Compare with tolerance, not `==`.

## Statistical noise dominates short runs

**Status**: Math
**Description**: For steady-state metrics, run long enough that the
estimator converges. Rule of thumb: 10000+ events for queueing.
Discard a warm-up period (first 5-10%) for tighter estimates.

## random.seed must be set before env.process

**Status**: Reproducibility
**Description**: `random.seed(42)` should come BEFORE the first
`env.process(...)`, otherwise initial sample is non-deterministic.

## Resource.request() must be released

**Status**: Convention
**Description**: Always use `with server.request() as req: yield req`.
A bare `req = server.request(); yield req` works but leaks if you
forget to release.

## Container.put / .get block when full / empty

**Status**: API design
**Description**: This is intentional — they are events. To non-blocking
check, use `len(container.put_queue)` or check `container.level`.

## Long-running env.run() is single-threaded

**Status**: Performance
**Description**: SimPy is pure Python single-thread. For >1M events,
profile with cProfile and avoid `print()` inside hot processes.
