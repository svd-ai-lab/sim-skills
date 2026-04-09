---
name: ansa-sim
description: Use when running BETA CAE ANSA pre-processor scripts through sim in headless batch mode (`ansa64.bat -execscript -nogui`). Phase 1 covers batch `.py` execution only — no persistent session, no GUI, no `.ansa` database manipulation without a script wrapper.
---

# ansa-sim

You are connected to **BETA CAE ANSA** via sim-cli. This file is the
**index**. It tells you where to look for actual content — it does not
contain the content itself.

The `/connect` response told you which active layer applies via:

```json
"skills": {
  "root":               "<sim-skills>/ansa",
  "active_sdk_layer":   null,        // ANSA has no Python SDK importable from outside
  "active_solver_layer":"25.0"       // or "24.1" / "23.1"
}
```

Always read `base/`, then your active `solver/<version>/`. There is no
`sdk/` overlay because the ANSA `ansa` Python module only loads inside
an ANSA-spawned interpreter — there's nothing pip-installable to pin.

---

## base/ — always relevant

| Path | What's there |
|---|---|
| `base/reference/` | Patterns for writing ANSA Python scripts that will be executed via `-execscript "script.py|main()"`. Common imports, exit conventions, error surfacing. |
| `base/spec/` | The contract this skill commits to (Phase 1 scope, what's in/out of scope). |
| `base/docs/` | Background notes, links to BETA documentation. |
| `base/skill_tests/` | Skill QA cases. |
| `base/known_issues.md` | Vendor quirks (path-handling oddities, license behavior). |

## solver/<active_solver_layer>/ — release specifics

Empty stubs by default; per-release deltas land here as discovered.

- `solver/25.0/notes.md` — current
- `solver/24.1/notes.md`
- `solver/23.1/notes.md`

## Hard constraints

1. **Phase 1 is one-shot only.** No persistent sessions. Every `sim
   exec` payload starts a fresh ANSA process via `-execscript`. State
   does not survive across calls; if you need state, write a single
   bigger script.
2. **`main()` is required.** ANSA's `-execscript "script.py|main()"`
   syntax expects an entry function. Don't write top-level statements
   that need to run; put them inside `def main():`.
3. **Acceptance ≠ exit code.** Always extract a structured artifact
   (a JSON line, a written file path) and validate against the user's
   criterion.

---

## Required protocol (one paragraph)

After `/connect` succeeds, validate Category A inputs (input geometry,
output target, acceptance criteria), then send the Python script via
`sim exec`. The driver shells out to `ansa64.bat -execscript
"<tmp>.py|main()" -nogui`. Parse the script's structured output and
evaluate against the user's acceptance criterion.
