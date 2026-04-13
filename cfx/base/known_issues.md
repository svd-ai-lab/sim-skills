# CFX Known Issues

## KI-001: cfx5solve stdout is empty

**Symptom**: `sim run` returns empty stdout, even though the solve completed.

**Cause**: CFX solver writes its output to `<name>_NNN.out` files, not to stdout/stderr. The `cfx5solve` executable itself produces minimal console output.

**Workaround**: Parse the `.out` file directly for convergence information. The driver's `parse_output()` handles JSON lines but CFX-specific parsing (iterations, residuals) requires reading the `.out` file.

## KI-002: CCL `Variable` vs `Colour Variable` in CFD-Post

**Symptom**: `cfx5post -batch` fails with "Parameter 'Variable' is not allowed in /CONTOUR:..."

**Cause**: CFD-Post contour objects use `Colour Variable`, not `Variable`.

**Fix**: Always use `Colour Variable = Pressure` in CONTOUR blocks.

## KI-003: cfx5cmds cannot modify mesh-related parameters

**Symptom**: `cfx5cmds -write` silently ignores changes to Location, mesh interfaces, or domain topology.

**Cause**: `cfx5cmds` can only modify physics CCL parameters (boundary conditions, solver settings, materials). Changes that affect mesh-CCL mapping require `cfx5pre`.

**Workaround**: Use `cfx5pre -batch` with a session file for mesh-related changes.

## KI-004: Chinese locale affects `.out` file parsing

**Symptom**: On Chinese Windows (locale zh-CN), some `.out` file sections may contain localized strings.

**Cause**: CFX solver uses system locale for some output formatting.

**Workaround**: Parse numeric patterns (residuals, iteration counts) with locale-independent regex. Avoid relying on English text labels.

## KI-005: cfx5solve -batch produces two result sets on re-run

**Symptom**: Running `cfx5solve -batch -def 015.def` twice produces `015_001.res` and `015_002.res`.

**Cause**: CFX auto-increments the run number. Each solve creates a new `_NNN` suffix.

**Workaround**: Always use the highest-numbered `.res` file for post-processing. Sort by name or modification time.

## KI-006: Unicode checkmark in sim CLI output fails on GBK locale

**Symptom**: `sim lint` crashes with `UnicodeEncodeError: 'gbk' codec can't encode character '\u2713'`

**Cause**: The `sim` CLI uses Unicode checkmarks (✓) that are not in the GBK character set used by Chinese Windows consoles.

**Workaround**: Use `sim --json lint` for machine-readable output that avoids Unicode display issues.

## KI-007: Post-processing `Location List` must match exact boundary names

**Symptom**: CFD-Post session file fails with "Object not found" error.

**Cause**: The `Location List` value must exactly match a boundary name from the CFX model (case-sensitive, including spaces).

**Workaround**: Check boundary names in the `.out` file's "BOUNDARY" sections, use `query("session.boundaries")` in session mode, or use `All Domains` for domain-wide contours.

## KI-008: cfx5post -line headless rendering shows wireframe only

**Symptom**: Images exported via session mode (`cfx5post -line` + `HARDCOPY` + `>print`) show wireframe geometry without filled contour colors.

**Cause**: `cfx5post -line` uses software rendering in headless mode, which doesn't fully render filled contour surfaces. The batch mode (`cfx5post -batch`) uses a different rendering pipeline.

**Solution (implemented in driver)**: Driver 自动采用 hybrid 模式——检测到 HARDCOPY + >print 时，将 session 中积累的 CCL history（CONTOUR 定义等）重放到临时 `.cse`，调用 `cfx5post -batch` 渲染。对 agent 透明，无需手动处理。详见 `reference/session_workflow.md`。

## KI-009: cfx5pre -line `enterccl` requires `.e` to submit

**Symptom**: CCL sent via `cfx5pre -line` doesn't take effect.

**Cause**: After entering CCL mode with `e` command, the CCL text is buffered. Must type `.e` to process it, or `.c` to cancel.

**Workaround**: Always end CCL input with `.e` on a separate line. The driver's `send_ccl()` method handles this automatically.

## KI-010: Perl `evaluate()` uses `chr(64)` for @ symbol

**Symptom**: `evaluate('massFlow()@inlet')` fails with Perl syntax error because `@inlet` is interpreted as a Perl array.

**Cause**: In Perl, `@` starts an array variable. CFX's evaluate function uses `@` as "at location" separator.

**Workaround**: Use `chr(64)` for the @ character: `evaluate('massFlow()'.chr(64).'inlet')`. The driver's `evaluate()` method handles this automatically.

## KI-011: cfx5pre -line does not accept raw CCL object definitions

**Symptom**: Typing `LIBRARY:` directly at the `CFX>` prompt gives "Action LIBRARY: is not recognized".

**Cause**: `cfx5pre -line` accepts session commands (`e`, `s`, `d`, `h`, `q`, `calc`, `!`), not raw CCL. CCL must be entered via the `e` (enterccl) command.

**Workaround**: Use `e` to enter CCL mode, then type CCL, then `.e` to submit.
