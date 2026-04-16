# ICEM CFD 24.1 (2024 R1) notes

## Install layout (Windows)

```
E:\Program Files\ANSYS Inc\v241\icemcfd\
└── win64_amd\
    ├── bin\
    │   ├── icemcfd.bat      ← batch-mode launcher
    │   ├── med.exe           ← GUI
    │   ├── med_batch.exe     ← headless batch runner
    │   └── auto_mesher.exe   ← automated meshing
    ├── icemcfd\
    │   ├── output-interfaces\  ← 143 solver export .tcl modules
    │   ├── blocking-interfaces\
    │   │   └── IcemHexaBlockingHarness\BlockingHarness-Python\
    │   └── lib\                ← Tcl libraries
    └── help\
        ├── library\            ← API docs (domainlib, topolib, etc.)
        └── output\             ← Export format specs
```

Environment variable: `ICEMCFD_ROOT241=E:\Program Files\ANSYS Inc\v241\icemcfd`

## Verified

| Capability | Status |
|---|---|
| `sim check icem` | ✅ detects 24.1 via ICEMCFD_ROOT241 |
| detect/lint for .tcl scripts | ✅ 15 unit tests pass |
| `sim run` smoke test | ✅ converged 1.7s, Tcl 8.4.11, JSON parsed |

## Known quirks

- `med_batch.exe` outputs license info then Tcl `puts` output on stdout.
- First license checkout adds ~60s overhead; subsequent runs use cached
  license (~1.7s).
- Tcl version is actually **8.4.11** (not 8.3.3 as documented).
- `ic_batch_mode` takes NO arguments (not `ic_batch_mode 1`).
- Must invoke via `cmd /c icemcfd.bat -batch -script` on Windows — calling
  `med_batch.exe` directly from MSYS2/bash hits missing DLL errors.
