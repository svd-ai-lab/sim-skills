# Known Issues — SfePy Driver

## API churn between versions

**Status**: Watch
**Description**: SfePy releases on a yearly cadence (`2023.x`, `2024.x`,
`2025.x`). The Problem / state-handling APIs are mostly stable but have
moved slowly. This driver is verified on 2025.4. Older notes elsewhere
on the web may use deprecated `pb.create_state()` etc.

## State retrieval: `state.get_state_parts()`

**Status**: API quirk
**Description**: After `state = pb.solve()`, retrieve DOF arrays via
```python
sol = state.get_state_parts()['u']
```
Direct attribute access (`state.u`) does not work in 2025.x.

## Region selector strings are NOT Python expressions

**Status**: API design
**Description**: `'vertices in (x < 0.001)'` is parsed by SfePy's own
mini-DSL. Things like `np.where(...)` or arbitrary lambdas inside the
selector string raise. Use `'vertices by callable'` mode for arbitrary
predicates.

## Verbose stdout

**Status**: Cosmetic
**Description**: SfePy logs many `sfepy: ...done` lines per solve.
Driver's `parse_output` ignores them; just emit a final JSON line.

## Heavy import time

**Status**: Performance
**Description**: `import sfepy` pulls in a lot. Cold start ~1-2 s.
Acceptable for one-shot, but factor in for benchmarking.

## Mesh formats

**Status**: Bridge
**Description**: SfePy reads `.mesh`, `.vtk`, `.msh` (Gmsh) directly,
plus more via internal converters. For exotic formats, route through
`meshio` first.
