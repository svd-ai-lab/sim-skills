# CFX 24.1 (2024 R1) Solver Notes

## Installation

- Path: `E:\Program Files\ANSYS Inc\v241\CFX\bin\`
- Environment variable: `AWP_ROOT241`
- CCL version range supported: 19.0 — 24.1

## CLI tools available

| Tool | Path |
|------|------|
| cfx5solve | `v241/CFX/bin/cfx5solve.exe` |
| cfx5pre | `v241/CFX/bin/cfx5pre.exe` |
| cfx5post | `v241/CFX/bin/cfx5post.exe` |
| cfx5cmds | `v241/CFX/bin/cfx5cmds.exe` |
| cfx5perl | `v241/CFX/bin/cfx5perl.exe` |
| cfx5mondata | `v241/CFX/bin/perllib/cfx5mondata.pl` |

## Perl modules

35 Perl modules in `perllib/`, including:
- `cfx5solve.pl` — solver wrapper
- `cfx5mondata.pl` — convergence data export
- `cfx5params.pl` — parameter editor
- `cfx5export.pl` — data export
- `cfx5stop.pl` — graceful solver stop

## Known quirks on 24.1

1. **Chinese locale**: `.out` file may contain mixed Chinese/English text. Parse by numeric patterns only.
2. **Auto-increment run number**: Each `cfx5solve` creates `_001`, `_002`, etc. No option to override.
3. **GBK console encoding**: sim CLI Unicode characters (✓, ✗) fail on Chinese Windows. Use `--json` mode.
4. **Large `.res` files**: VMFL015 produces 92 MB results for a small pipe flow. Plan disk space accordingly.
5. **CCL version compatibility**: .ccl files with `Version = 19.3` run fine on 24.1 solver (backwards compatible).
