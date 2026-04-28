# Known Issues — scikit-fem Driver

## Pure Python = performance ceiling

**Status**: By design
**Description**: scikit-fem is 100% Python (with numpy/scipy). For
problems > 100k DOFs, matrix assembly and solve time grow significantly.
For production-scale FEM, switch to FEniCS/dolfinx (C++) or OpenFOAM.

## External mesh loading needs meshio

**Status**: User-input driven
**Description**: `MeshTri.load("foo.msh")` requires `pip install meshio`.
The bare `scikit-fem` pip install doesn't pull this in. If loading Gmsh
or external meshes, add `meshio` to the environment:
```
pip install meshio
```

## `condense` tuple unpacking

**Status**: Common gotcha
**Description**: `condense(A, b, D=D)` returns a 3-tuple that must be
unpacked with `*` when passing to `solve()`:
```python
x = solve(*condense(A, b, D=D))        # CORRECT
x = solve(condense(A, b, D=D))         # TypeError
```

## Form decorator order matters

**Status**: By design
**Description**: `@BilinearForm` expects `(u, v, w)`, `@LinearForm`
expects `(v, w)`. Swapping gives cryptic TypeError inside `asm()`.

## Dirichlet projection for non-zero BCs

**Status**: User-input driven
**Description**: For non-zero Dirichlet, use `basis.project(lambda w:
...)` to get a coefficient vector representing the BC function, then
pass it as `x=...` in `condense`. Omitting this gives homogeneous u=0
boundary silently.
