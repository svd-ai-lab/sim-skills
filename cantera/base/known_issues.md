# Known Issues — Cantera Driver

## XML mechanism format deprecated

**Status**: Watch
**Description**: Pre-2.5 Cantera used `.cti` and `.xml` mechanism files.
2.6+ uses `.yaml`. The bundled `gri30.yaml`, `h2o2.yaml`, `air.yaml`
work out of the box. If a user provides a `.cti`, convert with
`ck2yaml` / `cti2yaml` first.

## Property setters are tuple assignments

**Status**: API design
**Description**: `g.TPX = 300, p, 'CH4:1'` works; `g.TPX(300, p, 'CH4:1')`
does not. Common new-user mistake.

## Bare Reactor doesn't integrate

**Status**: API design
**Description**: `IdealGasReactor(g)` alone has no integrator. Must
wrap in `ReactorNet([reactor])` and call `net.advance(t)` or
`net.step()`.

## `equilibrate` modes are case-sensitive

**Status**: API quirk
**Description**: `'HP'`, `'TP'`, `'SP'`, `'UV'` — uppercase. Lowercase
errors silently in some 2.x builds.

## Free flame may need `auto=True`

**Status**: Convergence aid
**Description**: For premixed flames, `f.solve(auto=True)` enables
the auto-restart strategy (start with no chemistry, refine, then add
energy equation). Without it, cold starts often fail.

## Heavy mechanism load time

**Status**: Performance
**Description**: `Solution('gri30.yaml')` ~50 ms, but bigger mechanisms
(USC-II, Aramco) take 1-2 s. Cache the Solution instance across calls
when possible.

## YAML file lookup path

**Status**: User error
**Description**: Cantera searches its data dir then cwd. Custom paths:
```python
ct.add_directory('/path/to/mechanisms')
g = ct.Solution('mymech.yaml')
```
