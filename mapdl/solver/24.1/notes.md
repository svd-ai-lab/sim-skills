# MAPDL 24.1 (2024 R1) notes

## Install layout (Windows, default)

```
E:\Program Files\ANSYS Inc\v241\
├── ansys\bin\winx64\ANSYS241.exe    ← launched by launch_mapdl()
├── ansys\bin\winx64\MAPDL.exe       ← alias, same executable
├── aisol\                             ← Mechanical app bits (unrelated)
├── CFX\                               ← CFX bits
└── licensingclient\                   ← license client
```

Environment var: `AWP_ROOT241=E:\Program Files\ANSYS Inc\v241`.

## Verification status

| Workflow | Status | Reference |
|---|---|---|
| `launch_mapdl()` auto-detect | ✅ verified | — |
| Static structural (2D I-beam) | ✅ verified | `workflows/mapdl_beam/` |
| Static structural (3D notched plate) | ✅ verified, K_t ≈ 1.60 | `workflows/notch_3d/` |

## Known 24.1 quirks

- **Licence locale**: `AWP_LOCALE241=zh` on CJK Windows affects
  MAPDL's own log formatting (header strings become GB-encoded).
  Does **not** affect gRPC traffic — the wire protocol is UTF-8.
  If you capture stdout from the `ANSYS241.exe` child process and
  pipe it into anything assuming UTF-8, expect mojibake.
- **License server**: `ANSYSLMD_LICENSE_FILE=1055@LOCALHOST` expected.
  `launch_mapdl()` blocks for ~5s on first invocation if the license
  server handshake is slow.
- **Startup time**: cold start ~6–10 s on Windows (first call),
  ~2–4 s on subsequent calls (Windows caches the exe).

## Not-yet-verified

- Harmonic response
- Cyclic symmetry
- Nonlinear contact
