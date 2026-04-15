# MAPDL known issues

Failure modes discovered during skill / driver TDD.

## KI-001 — `ansys-tools-path` DeprecationWarning

**Symptom**: On any PyMAPDL call that resolves the MAPDL exe:
```
DeprecationWarning: This library is deprecated and will no longer be
maintained. Functionality from this library has been migrated to
``ansys-tools-common``.
```

**Status**: Noise. Functionally works. PyMAPDL 0.72 still uses
`ansys.tools.path.find_mapdl` internally.

**Workaround**: `warnings.filterwarnings("ignore", category=DeprecationWarning)`
at the top of snippets if the noise is disruptive.

## KI-002 — First-ever `launch_mapdl()` may prompt interactively

**Symptom**: On a fresh machine with no `AWP_ROOT<xxx>` env var and
no cached `~/.ansys/config.txt`, `launch_mapdl()` prompts
`Enter location of MAPDL executable:` and blocks.

**Impact**: Breaks non-interactive pipelines (CI, sim server, agent
scripts).

**Mitigation**:
- Always set `AWP_ROOT<xxx>` system-wide. The Ansys installer does
  this by default on Windows.
- For one-time setup on a new user account:
  ```python
  from ansys.mapdl import core as pm
  pm.change_default_ansys_path(r"E:\Program Files\ANSYS Inc\v241\ansys\bin\winx64\ansys241.exe")
  ```
- In snippets, pass `exec_file=...` explicitly.

## KI-003 — Zombie `ANSYS<ver>.exe` on exception

**Symptom**: Script raises before `mapdl.exit()` → the MAPDL solver
keeps running in the background, holding a license.

**Fix**: Use `with launch_mapdl() as mapdl:` or wrap in
`try/finally` with `mapdl.exit()` in finally. The sim driver's
subprocess execution isolates this — a single snippet failure
can't leak between `sim run` invocations.

## KI-004 — Mid-side nodes have NaN stress

**Symptom**: `np.max(stress)` returns `nan` on quadratic meshes
(SOLID186, PLANE183).

**Fix**: Always use `np.nanmax` / `np.nanmean` for aggregates:
```python
max_stress = np.nanmax(von_mises)
```

## KI-005 — `mapdl.set(1, 1)` mandatory in POST1

**Symptom**: All displacement / stress queries return zero-filled
arrays, no error raised.

**Fix**: Add `mapdl.set(1, 1)` (or appropriate LS/SS) immediately
after `mapdl.post1()`.

## KI-006 — `mapdl.allsel()` before solve

**Symptom**: Solver runs but solves only a subset of the model
because a BC `nsel` subselected the model and `allsel` was missed.

**Fix**: Always call `mapdl.allsel()` (or `mapdl.allsel(mute=True)`)
immediately before `mapdl.solve()`.

## KI-007 — DeprecationWarning from `ansys-mapdl-reader`

**Symptom**: Using `mapdl.result` (which routes through
`ansys-mapdl-reader`) prints:
```
PyVistaFutureWarning: The default value of `algorithm` for the
filter `UnstructuredGrid.extract_surface` will change in the future.
```

**Status**: Noise. Plots render correctly.

## KI-008 — `vtk.libs` DLL file-lock during pip install

**Symptom**: `uv pip install ansys-mapdl-core` fails with:
```
failed to copy file from ... vtk.libs\msvcp140-...dll: 另一个程序正在使用此文件
```

**Cause**: A concurrent Python process has `vtk` imported.

**Fix**: Close all Python processes (including dormant Jupyter
kernels), then retry. `export UV_LINK_MODE=copy` to avoid
hardlinking issues on cross-filesystem installs.
