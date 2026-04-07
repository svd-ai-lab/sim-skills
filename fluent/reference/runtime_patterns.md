# Runtime Control Patterns — fluent-sim v0

> These are **control patterns**, not code templates.
> Each pattern describes agent decision logic, not Python syntax.

---

## Pattern 0 — Session Lifecycle

```
CONNECT → [STEP × N] → DISCONNECT
```

- One session per task. Do not reuse a session across unrelated tasks.
- Connect with the correct `--mode` (meshing vs. solver). Mode cannot change mid-session.
- Always disconnect explicitly, even if steps failed.

---

## Pattern 1 — Connect + Verify

**When**: At the start of every task.

**Actions**:
1. Run `sim connect --mode <mode> --ui-mode <ui_mode> --processors <N>`
2. Check exit code = 0
3. Run `sim query session.summary`
4. Verify: `connected=true`, `mode=<expected>`, `run_count=0`

**If verification fails**: Stop. Report to user. Do not proceed with workflow steps.

---

## Pattern 2 — Step Execution Loop

**When**: For each workflow step.

```
write code → sim run --code-file <tmp> --label <label>
         ↓
     exit code?
       0 → query last.result → ok=true? → continue
                                        → ok=false? → STOP, report
       ≠0 → STOP, report
```

**Key principle**: Each step is a checkpoint. The loop does not advance until the current step is confirmed successful.

**Label convention**: Use descriptive labels (`init-workflow`, `import-geometry`, `surface-mesh`, etc.). Labels appear in `session.summary.run_count` and log files — they are the audit trail.

---

## Pattern 3 — State Query

**When**: After any step that changes session state, or when verifying a precondition.

Available queries:

| Query | Returns | Use when |
|---|---|---|
| `sim query session.summary` | `connected`, `mode`, `run_count` | Verifying session health, counting completed steps |
| `sim query last.result` | `ok`, `label`, `result`, `stdout`, `stderr` | Checking step outcome and extracted values |
| `sim query workflow.summary` | Workflow task list and states | Debugging meshing workflow task sequence |
| `sim query field.catalog` | Available fields/variables | Pre-processing before result extraction |

**Do not skip queries** between steps that depend on each other. For example: do not send the volume mesh step before confirming the surface mesh step succeeded.

---

## Pattern 4 — Acceptance Evaluation

**When**: After the final step of a workflow.

**Actions**:
1. Run `sim query session.summary` → verify `run_count` matches expected step count
2. Run `sim query last.result` → verify `result` object contains expected fields
3. Compare extracted values against the acceptance checklist for this workflow type
4. If all criteria pass → task is COMPLETE
5. If any criterion fails → task is INCOMPLETE, report which criteria failed

**Critical distinction**:
- "The script ran without error" ≠ task complete
- "The acceptance checklist is satisfied" = task complete

---

## Pattern 5 — Failure Handling

**When**: Any step fails (non-zero exit, `ok=false`, exception in stderr).

**Actions**:
1. Read `last.result.stderr` for the exception message
2. Read `last.result.stdout` for any partial output
3. Check `session.summary.run_count` to confirm which steps completed
4. Do NOT silently retry. Report to user with:
   - Which step failed
   - The error message
   - Steps completed before the failure
   - Whether the session is still alive (can the user inspect it?)

**Do not attempt automated error recovery in v0.** Recovery strategies are a v1 concern.

---

## Pattern 6 — Disconnect + Report

**When**: At the end of every task (success or failure).

**Actions**:
1. Run `sim disconnect`
2. Report to user:
   - Workflow type and mode
   - Steps completed (labels, run_count)
   - Key extracted values (cell count, residuals, mass flow rate, etc.)
   - Whether acceptance criteria were satisfied
   - Any warnings or non-fatal issues observed in stdout

**Format**: Structured summary, not a narrative. Values should be explicit.

---

## Pattern 7 — Multi-Step Dependency Ordering

**Rule**: Never send step N+1 before step N is confirmed successful.

**Common dependency chains**:

Meshing (watertight):
```
InitializeWorkflow → ImportGeometry → LocalSizing → SurfaceMesh
→ DescribeGeometry → UpdateBoundaries → UpdateRegions
→ BoundaryLayers → VolumeMesh → SwitchToSolver
```

Solver:
```
ReadCase → ReadData → MeshCheck → Iterate → ExtractResults
```

If a step is skippable (e.g., LocalSizing defaults are acceptable), explicitly note that it was skipped and why.
