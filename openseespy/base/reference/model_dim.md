# `ndm` and `ndf` — model dimensions and DOFs per node

Set once via `ops.model('basic', '-ndm', N, '-ndf', M)`. **Every** later
`node`, `fix`, and `load` call must match the chosen `ndf`.

| ndm | ndf | Use case | DOF layout |
|---|---|---|---|
| 1 | 1 | 1D bar, axial only | (ux) |
| 2 | 2 | 2D truss | (ux, uy) |
| 2 | 3 | 2D frame (Euler-Bernoulli or Timoshenko beam) | (ux, uy, rotz) |
| 3 | 3 | 3D truss / continuum brick | (ux, uy, uz) |
| 3 | 6 | 3D frame | (ux, uy, uz, rotx, roty, rotz) |

Mismatch examples — silent bugs:

```python
ops.model('basic', '-ndm', 2, '-ndf', 3)   # frame
ops.fix(1, 1, 1)                            # WRONG: only 2 fix flags, expected 3
                                            # rotz silently free → unrealistic
                                            # base motion in beam analyses

ops.model('basic', '-ndm', 2, '-ndf', 2)   # truss
ops.load(2, 0.0, -1000.0, 100.0)            # WRONG: 3rd term ignored
                                            # but no error reported
```

When in doubt: write a tiny `ops.fix` / `ops.load` with the wrong number
of args and OpenSees raises — easy to verify before scaling up.
