# SimPy 4.x Notes

## Provenance

- Source: PyPI `simpy`
- Verified version: 4.0.2
- Pure Python, no compiled deps

## Capabilities verified

| Feature | Status | Notes |
|---------|--------|-------|
| `simpy.Environment()` | Verified | |
| `env.timeout(t)` | Verified | |
| `env.process(generator)` | Verified | |
| `simpy.Resource(env, capacity=N)` | Verified | M/M/1 use case |
| `with resource.request() as req: yield req` | Verified | release on exit |
| `env.run(until=T)` | Verified | float time |

## M/M/1 benchmark

λ=2, μ=3, T=10000, seed=42:
L_observed=1.96 vs theory 2.00 (1.9% err)
Wq_observed=0.65 vs theory 0.667 (2.5% err)
~20000 customers processed.

## Version detection

```bash
python3 -c "import simpy; print(simpy.__version__)"
```
returns `4.0.2`. Driver normalizes to `4.0`.

## Differences vs SimPy 3.x

3.x had a procedural-style `simpy.Process(env, gen)` API. 4.x uses
`env.process(gen)`. Most public surface (Resource, Container, Store)
unchanged.
