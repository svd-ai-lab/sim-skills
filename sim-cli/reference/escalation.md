# Escalation — when to stop and report

Across all sim-cli drivers: **do not silently retry failed steps.**
Agents that burn through 50 retries leave the user with unusable session
state and no diagnostic signal. Stop early, report cleanly, let the
user decide.

---

## Stop-and-report triggers

Stop on any of these. Do not attempt automated recovery.

| Trigger | Signal |
|---|---|
| Driver unavailable | `sim connect` / `sim run` exits non-zero with "no driver for `<solver>`" or "solver not installed" |
| Runtime profile empty / unknown / deprecated | `sim inspect session.versions` returns `profile: null` or a value not in the driver's `compatibility.yaml` (see [`version_awareness.md`](version_awareness.md)) |
| Step failed (persistent) | `sim exec` non-zero exit, or `sim inspect last.result` returns `ok=false`, or `stderr` contains an exception |
| Step failed (one-shot) | `sim run` non-zero exit, or `stderr` contains ERROR lines, or `parse_output(stdout)` returns `{}` when a payload was expected |
| Session state inconsistent | `sim inspect session.summary` shows unexpected `run_count` or `mode` after a step |
| Acceptance failed | After all steps succeeded, an acceptance criterion was not met — see [`acceptance.md`](acceptance.md) |

---

## What to report

Always include, in a structured summary:

1. **What was attempted** — solver, workflow, the failing step's label.
2. **The error signal** — exit code, first ~20 lines of `stderr`,
   exception class and message if present.
3. **Completion state** — how many steps succeeded before the failure
   (`session.summary.run_count` for persistent; "reached step N of M"
   for one-shot).
4. **Session liveness** — for persistent sessions, whether the session
   is still alive (`sim inspect session.summary → connected`). If it
   is, the user can inspect it manually before you disconnect.
5. **What would need to change to try again** — a missing input, a
   different mode, an incompatible SDK version, a corrupted file.

Format example (persistent):

```
[sim] FAILED at step 4/8 (label="setup-material")
  error: AttributeError: 'FluentSettings' has no attribute 'general'
  session: connected=true, mode=solver, run_count=3
  stdout (last 5 lines): …
  stderr (last 5 lines): …

Likely cause: PyFluent 0.37 dialect used against 0.38 runtime.
The active_sdk_layer returned by Step-0 was "pyfluent-0.37"
but the snippet is from base/snippets/ (0.38 dialect).
To proceed: either swap to sdk/pyfluent-0.37/snippets/, or upgrade
the environment to pyfluent 0.38.
```

Format example (one-shot):

```
[sim] FAILED (exit=2) during sim run analysis.m --solver matlab
  stderr: Undefined function 'cfd_solve' for input arguments of type 'double'.
  stdout: (empty)

Likely cause: cfd_solve is not on the MATLAB path in the current environment.
To proceed: either add the toolbox containing cfd_solve to the MATLAB
path, or supply a script that uses a built-in solver.
```

---

## What *not* to do

- ❌ Silently retry with different parameters ("maybe it'll work this
  time").
- ❌ Disconnect the session before the user has had a chance to inspect
  it — if it is still alive, leave it alive.
- ❌ Edit the user's input files to "fix" the error. If inputs are
  wrong, ask the user.
- ❌ Swap to a different solver because the current one failed. The
  user picked this solver; respect that.
- ❌ Claim success because "the exit code was 0" when an acceptance
  criterion was not met. See [`acceptance.md`](acceptance.md).

---

## Automated recovery is out of scope

v0 sim-cli skills do **not** attempt automated error recovery. Recovery
strategies (retry with different `--processors`, fall back to a simpler
mesh, switch from `pyfluent.launch_fluent` to `sim serve`, …) are a v1
concern and require explicit user opt-in.
