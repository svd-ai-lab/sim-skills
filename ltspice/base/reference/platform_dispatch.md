# Platform dispatch — when to use `--host <win1>`

LTspice has two very different install flavors. Pick the right one for
what you're doing.

## macOS native (LTspice 17.x)

- ✅ `.net` / `.cir` / `.sp` batch runs — fully supported
- ✅ `.meas` result extraction — fully supported
- 🟡 `.asc` input — only when schematic is flat + uses shipped library
  symbols (sim-ltspice's native asc2net handles these)
- ❌ Hierarchical `.asc`, custom `.subckt` symbols, `-ascii` raw
  output, `-netlist` schematic→netlist conversion

If `sim run my.asc --solver ltspice` raises `MacOSCannotFlatten`, your
schematic is hitting one of the ❌ cases above. Route via win1.

## Windows (LTspice 26.x)

- ✅ Everything. `.asc` input with any topology, `-netlist` pass,
  `-ascii` raw output, full batch surface.
- Reach it via `sim --host 100.90.110.79` (tailscale IP; see
  `../sim-cli/SKILL.md` for the HTTP dispatch model).

## Decision tree

```
.net input?  ────────────────→ Run local. macOS and Windows both fine.

.asc input + flat + library-only? ──→ Run local on Mac (native asc2net).
                                      Or on Win1 (uses LTspice -netlist).

.asc input + hierarchy / custom lib? ──→ Route via sim --host 100.90.110.79.

Need .raw in ASCII format? ──→ Win1 only (`-ascii` flag unsupported on Mac).

Need schematic→netlist conversion WITHOUT simulating?
                               ──→ Win1 only (`-netlist` is the command).
```

## One command covers both

```bash
# Auto-detect: local if possible, remote win1 otherwise.
# sim-cli handles the routing based on the input's requirements.
sim --host 100.90.110.79 run design.asc --solver ltspice
```

You can always use `--host 100.90.110.79` even for cases that would
work locally — it's the universal answer. Costs a round-trip; gains
feature parity.

## Why the difference?

LTspice's macOS native build is a direct port with a minimal command
surface (`-b` only). The full CLI — rotation of `-b` / `-Run` / `-netlist`
/ `-ascii` / `-FastAccess` / `-encrypt` / `-sync` — only exists on
Windows and in wine. This isn't a bug; Analog Devices explicitly
scoped the Mac native build as "batch-run-a-netlist and nothing
else." For full scripting, wine on macOS or a Windows host is the path.
