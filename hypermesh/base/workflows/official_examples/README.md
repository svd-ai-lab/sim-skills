# Official Examples E2E -- Evidence

> Verified: 2026-04-17, HyperWorks Desktop v2026.0.0.27, Windows 11
> Model: bumper.hm (Altair demo, 473 nodes / 436 elements / 5 components)

## Automation Chain

```
runhwx.exe ... -startwith HyperMesh -f run_all.py
  -> HyperWorks Launcher (hwx.exe)
    -> SetForegroundWindow + SendKeys {ENTER} (auto Create Session)
      -> HyperMesh initializes
        -> -f run_all.py auto-executes
          -> 4 official examples run sequentially
```

## Results: 4/4 PASS

| Example | Description | Key Result |
|---------|-------------|------------|
| Ex01 | Create entities | 473 nodes, 436 elements, Steel MAT1 created |
| Ex02 | Modify entities | Material E=210000, Nu=0.3, element 18 isolated (QUAD4) |
| Ex05 | CoG nodes | 5 components, 5 CoG nodes created with valid 3D coords |
| Ex06 | Solid components | n_solids=0 (shell model, correct) |

## Evidence

- `e2e_evidence_bumper.png` -- HyperMesh GUI with bumper model loaded,
  constraints and loads visible, Python console showing execution log
- `ex01_result.json` through `ex06_result.json` -- individual results
- `e2e_summary.json` -- aggregate summary

## Scripts Adapted From

https://help.altair.com/hwdesktop/pythonapi/hypermesh/examples/hm_examples.html

Examples 03 and 04 were skipped because:
- Ex03 requires `pedal.hm` (not in local demos) + interactive GUI selection
- Ex04 requires interactive element selection (`CollectionByInteractiveSelection`)
