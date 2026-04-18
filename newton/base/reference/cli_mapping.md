# newton-cli → sim CLI mapping

The standalone `newton-cli` binary exposes 10 subcommands. This table shows how each maps onto sim when using the `newton` driver.

| newton-cli | sim equivalent | Status (v1) |
|---|---|---|
| `newton-cli version` | `sim check newton` | ✓ — reports newton + warp version via `connect()` |
| `newton-cli devices list` | part of `sim check newton` | Partial — top install's device list surfaces in `extra` |
| `newton-cli api list [--module M]` | `sim inspect api.list` | **v2** — module exists (`sim.drivers.newton.introspect`) but not wired yet |
| `newton-cli api describe <symbol>` | `sim inspect api.<symbol>` | **v2** — same module |
| `newton-cli model build --recipe R --out O` | built into `sim run recipe.json` | ✓ — no separate build step, recipe is the model |
| `newton-cli sim run --model M --solver S --out O` | `sim run recipe.json --solver newton` | ✓ — env vars control solver/frames/fps/substeps |
| `newton-cli viewer render --model M --state S --out O` | — | **out of scope (v1)** |
| `newton-cli run-script script.py` | `sim run script.py --solver newton` | ✓ — artifact dir contract preserved |
| `newton-cli examples list` | browse `newton.examples` via `sim inspect` | **v2** |
| `newton-cli examples run <name>` | run via Route B script that wraps `newton.examples.main()` | ✓ — see `workflows/cable_twist/` for the pattern |

## Key divergences

1. **No standalone `model build`**: the recipe IS the model. `sim run recipe.json` validates on load and fails fast if the recipe is malformed.
2. **One envelope schema**: sim uses `sim/newton/v1` everywhere. newton-cli's `newton-cli/v1` schema is not re-emitted — the driver translates at the boundary.
3. **Artifact env var**: both `SIM_ARTIFACT_DIR` and `NEWTON_CLI_ARTIFACT_DIR` are set to the same path, so existing newton-cli run-scripts work unchanged.
4. **No `--json` flag**: sim always emits structured output on `sim <...> --output json` or lets the driver-side envelope speak for itself via `parse_output`.
