# Operators and apply

## Building an Operator

```python
op = Operator(
    [stencil1, stencil2, ...],     # list of Eq
    name='Kernel',                  # optional
    subs=grid.spacing_map,          # symbolic spacing → numeric
)
```

On first `op.apply(...)`, Devito generates and JIT-compiles C code in
the cache dir (`~/.devito` or `$DEVITO_AUTOTUNING`). Subsequent calls
reuse the compiled binary.

## apply

```python
op.apply(time_M=200, dt=0.001)              # 0..200 timesteps
op.apply(time_m=10, time_M=100, dt=dt)      # subset
op.apply(time=200, dt=dt, x_M=80, y_M=80)   # also restrict spatial range
```

Devito recognizes any `Constant` / `Symbol` argument as overridable
at apply time:
```python
alpha = Constant(name='alpha')              # placeholder
eq    = Eq(u.dt, alpha * u.laplace)
op    = Operator([Eq(u.forward, solve(eq, u.forward))])
op.apply(time_M=100, dt=0.001, alpha=0.1)  # bind alpha at run
```

## solve

`solve(eq, target)` rearranges the equation symbolically to express
`target` (typically `u.forward`) explicitly. Required for explicit
schemes; not needed for fully prescribed updates like `Eq(u.forward, expr)`.

## Performance knobs

| Knob | Effect |
|---|---|
| `space_order=8` on Function | higher-order stencil, more flops |
| `op.apply(autotune=True)` | runtime tile-size search (slow first call) |
| `DEVITO_LANGUAGE=openmp` env var | enable OpenMP threading |
| `OMP_NUM_THREADS=N` | thread count |
| `DEVITO_PLATFORM=cpu64` (or `nvidiaX`) | target architecture |

## Profiling

```python
from devito import configuration
configuration['log-level'] = 'PERF'
op.apply(time_M=100, dt=0.001)
# prints kernel timing breakdown
```
