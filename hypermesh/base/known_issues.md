# Known Issues -- HyperMesh Driver

## KI-001: HyperMesh not pip-installable

**Status**: By design
**Description**: The `hm` module is only available inside HyperMesh's
bundled Python interpreter. Cannot `pip install hm`.
**Workaround**: Must run scripts via `hw -b -script script.py` or
inside the HyperMesh GUI Python console.

## KI-002: InteractiveSelection fails in batch mode

**Status**: By design
**Description**: `CollectionByInteractiveSelection`,
`EntityByInteractiveSelection`, and `PlaneByInteractiveSelection`
require GUI interaction. They hang or fail in batch mode (`hw -b`).
**Fix**: Use programmatic collection creation instead:
`hm.Collection(model, ent.Element, [id_list])` or
`hm.FilterByAttribute(ent.Element, "config=104")`.

## KI-003: Popups block batch execution

**Status**: Known behavior
**Description**: Some operations trigger confirmation dialogs in the GUI.
In batch mode, these block indefinitely.
**Fix**: Pre-answer popups before operations:
```python
model.hm_answernext('yes')
model.deletemodel()
```

## KI-004: block_redraw required for batch performance

**Status**: Best practice
**Description**: Without `hm.setoption(block_redraw=1)`, batch scripts
run slowly due to GUI refresh attempts.
**Fix**: Always set at script start:
```python
hm.setoption(block_redraw=1, command_file_state=0, entity_highlighting=0)
model.hm_blockbrowserupdate(mode=1)
```

## KI-005: Entity config must be set at creation

**Status**: API constraint
**Description**: Some entities (loads, designpoints) have multiple
configurations. The configuration cannot be changed after creation.
Use the correct entity class: `ent.LoadForce` (config=1),
`ent.LoadMoment` (config=2), `ent.LoadConstraint` (config=3).

## KI-006: Collection entity type restriction

**Status**: API constraint
**Description**: A single Collection can only contain entities of one
type and from one model. Use CollectionSet for multi-type operations.

## KI-007: Version path detection on Windows

**Status**: Driver implementation
**Description**: HyperMesh install paths vary by version and licensing:
`C:\Program Files\Altair\2025\hwdesktop\hw\bin\win64\hw.exe`.
The driver scans `ALTAIR_HOME`, PATH, and Program Files.
**Workaround**: Set `ALTAIR_HOME` environment variable if auto-detection
fails.

## KI-008: Python 2 vs 3 compatibility

**Status**: Resolved in 2024+
**Description**: HyperWorks Desktop 2024+ uses Python 3.x.
Earlier versions may use Python 2.7. All snippets in this skill
assume Python 3.x.

## KI-009: Batch flag (-b) does NOT initialize HyperMesh

**Discovered**: 2026-04-17 (E2E on HyperWorks 2026.0.0.27)
**Status**: Architecture constraint
**Description**: `runhwx.exe ... -b -f script.py` launches Python
but does NOT initialize HyperMesh. `hm/__init__.py` checks for
`IsHyperMeshLoaded` in `__main__` and raises `ImportError:
HyperMesh is not initialized`. The `-b` flag skips GUI/engine init.
**Fix**: Do NOT use `-b` with Python scripts that `import hm`.
Instead, launch without `-b` and let the user Create Session in the
Launcher. The `-f script.py` flag auto-executes after session init.

## KI-010: Process name is hwx.exe, not hw.exe

**Discovered**: 2026-04-17
**Status**: Driver implementation detail
**Description**: The actual HyperMesh process is `hwx.exe` (HyperWorks
Desktop), not `hw.exe`. `runhwx.exe` is the launcher that starts
`hwx.exe`. `hw.exe` exists in the install tree but is not the correct
entry point for HyperMesh.

## KI-011: Create Session required before script execution

**Discovered**: 2026-04-17
**Status**: Architecture constraint
**Description**: `runhwx.exe -startwith HyperMesh -f script.py` opens
the HyperWorks Launcher screen. The user must click "Create Session"
to initialize HyperMesh. Only after session initialization does the
`-f script.py` auto-execute. This means fully unattended batch is
not possible with the current Python API.
**Workaround**: Pre-launch HyperMesh GUI, then use `File > Load >
Python Script` or `run "script.py"` in the IPython console.
