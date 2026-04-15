# OpenSeesPy 3.x Notes

## Provenance

- Source: PyPI `openseespy` + `openseespylinux`
- Verified version: 3.5.1.3
- Wheels include compiled OpenSees C++ core (no separate install needed)

## Capabilities verified on this build

| Feature | Status | Notes |
|---------|--------|-------|
| `ops.model('basic', '-ndm', 2, '-ndf', 3)` | Verified | 2D frame |
| `ops.node`, `ops.fix` | Verified | |
| `ops.geomTransf('Linear', ...)` | Verified | |
| `ops.element('elasticBeamColumn', ...)` | Verified | 2D, 7-arg form |
| `ops.timeSeries / pattern / load` | Verified | Linear + Plain |
| Static analysis chain | Verified | BandSPD/RCM/Plain/LoadControl/Linear |
| `ops.analyze(N)` | Verified | returns 0 on success |
| `ops.nodeDisp(node, dof)` | Verified | 1-indexed dof |

## Cantilever benchmark

L=1m, E=2e11, I=1e-6, P=-1000 N → tip = -1.6667e-3 m
(matches analytical to 1.3e-12 relative error).

## Version detection

Python 3.8+:
```bash
python3 -c "import importlib.metadata as md; print(md.version('openseespy'))"
```
Python 3.7:
```bash
python3 -c "import pkg_resources; print(pkg_resources.get_distribution('openseespy').version)"
```

## Known stderr noise

Every successful run prints `Process 0 Terminating` to stderr. The
driver's `parse_output` ignores it; downstream code should not key on
stderr cleanliness.
