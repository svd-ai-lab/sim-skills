# Known Issues — ansa-sim

## ISSUE-002: ANSA has no persistent session API

**Date discovered**: 2026-04-03
**Severity**: Informational — by design, not a defect
**Status**: Permanent limitation

### Details

ANSA does not provide any mechanism for external processes to connect to a running instance:
- No RPC/gRPC/REST/socket API
- No COM/DCOM automation object
- No daemon mode or server mode
- `ansa` Python module is only importable inside the ANSA process

This was confirmed through:
- Official BETA CAE documentation
- Community GitHub repos (sshnuke333/ANSA-Scripts, vahadruya skewed elements)
- Conference paper (Opel + BETA CAE pedestrian marking automation)
- KOMVOS framework analysis (batch dispatch only, no IPC bridge)

### Impact

The sim ANSA driver is limited to one-shot batch execution. Each `run_file()` call
launches a fresh ANSA process, executes the script, and exits. There is no
`connect/exec/disconnect` session lifecycle.

### Workaround (if needed in future)

A self-hosted socket server script could run inside ANSA's embedded Python (which
has access to `socket` and `threading` from stdlib). This is unofficial and untested.

---

## ISSUE-003: CreateEntity for GRID nodes returns None in empty model

**Date discovered**: 2026-04-03
**Severity**: Low — affects test script design
**Status**: Open

### Details

`base.CreateEntity(deck, "GRID", {"X": 0.0, "Y": 0.0, "Z": 0.0})` returns `None`
when called on an empty model with no geometry loaded. GRID creation likely requires
an existing face/surface context.

Other entity types (`PSHELL`, `MAT1`) create successfully without prerequisites.

### Impact

Test scripts that need mesh elements should either:
- Load an existing `.ansa` model first
- Use `PSHELL`/`MAT1` for entity creation tests (works)
- Use higher-level meshing APIs that create geometry first
