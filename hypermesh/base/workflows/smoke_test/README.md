# HyperMesh Smoke Test -- E2E Evidence

> Verified: 2026-04-17, HyperWorks Desktop v2026.0.0.27, Windows 11
> Execution: `runhwx.exe ... -startwith HyperMesh -f probe3.py`

## Key Discovery: Execution Architecture

HyperMesh Python API (`import hm`) requires a fully initialized
HyperMesh GUI session. The execution chain is:

```
runhwx.exe (launcher)
  → hwx.exe (HyperWorks Desktop process)
    → HyperMesh Launcher screen
      → User clicks "Create Session"
        → HyperMesh fully initializes
          → -f script.py auto-executes
            → import hm succeeds
```

**Batch mode (`-b`) does NOT work** for Python scripts because it
skips HyperMesh initialization. `hm/__init__.py` checks for
`IsHyperMeshLoaded` in `__main__` and raises `ImportError` if
HyperMesh is not running.

## Correct Command Line

```
runhwx.exe -client HyperWorksDesktop -plugin HyperworksLauncher \
  -profile HyperworksLauncher -l en -startwith HyperMesh \
  -f script.py
```

Extracted from the official HyperMesh 2026 desktop shortcut.

## Result

```json
{
  "ok": true,
  "n_materials": 1,
  "n_properties": 1,
  "mat_name": "Steel",
  "E": 210000.0,
  "Nu": 0.3,
  "thickness": 2.0
}
```

## What Was Tested

- `import hm` and `import hm.entities as ent` -- OK
- `hm.Model()` creation -- OK
- `ent.Material(model)` creation with MAT1 cardimage -- OK
- `ent.Property(model)` creation with PSHELL cardimage -- OK
- Material-to-property assignment via `prop.materialid = mat` -- OK
- `hm.Collection(model, ent.Material)` counting -- OK
- JSON result written to file -- OK

## What Failed

- `runhwx.exe -f script.py -b` -- Python executes but `import hm`
  fails: "HyperMesh is not initialized"
- `hmbatch.exe -tcl script.py` -- Tcl interpreter, rejects Python syntax
- `hw.exe -b -script script.py` -- Silent exit, no execution
