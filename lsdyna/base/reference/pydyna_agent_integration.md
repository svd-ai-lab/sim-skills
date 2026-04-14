# PyDyna Agent Integration

PyDyna ships **its own AI agent instruction files** that document the
`keywords` API in a format optimized for AI coding assistants
(GitHub Copilot, Cursor, Claude Code).

These files complement this `lsdyna` sim-skill — the sim-skill covers
*operational* concerns (when to use SDK vs hand-written `.k`, sim-cli
integration, output verification) while PyDyna's own agent files cover
*API mechanics* (every keyword class, every method, every pattern).

## Recommended setup for agents working in this repo

Run once in your project root:

```bash
python -m ansys.dyna.core agent --env claude --copy
```

This creates:
- `.agent/ansys.dyna.core.md` — main quick reference
- `.agent/ansys.dyna.core/deck.md` — full `Deck` class operations
- `.agent/ansys.dyna.core/keywords.md` — keyword creation patterns
- `.agent/ansys.dyna.core/patterns.md` — workflow examples
- `CLAUDE.md` — appended pointer (for Claude Code)

For Cursor: `--env cursor` creates `.cursor/rules/pydyna.mdc`.
For VS Code Copilot: `--env vscode` creates `.github/copilot-instructions.md`.

## What the bundled instructions cover

| Topic | Files |
|-------|-------|
| Deck operations: load, filter, modify, write | `deck.md` |
| Keyword usage: materials, sections, elements | `keywords.md` |
| Data access: direct attrs, DataFrames | `keywords.md` |
| Workflows: load→modify→save, build from scratch | `patterns.md` |
| Best practices: filtering, validation | `patterns.md` |

## Why use the bundled docs alongside this skill

The PyDyna instructions are **version-aligned** — they exactly match the
installed `ansys-dyna-core` version's API (auto-generated keyword names
can shift between releases). After every `pip install --upgrade
ansys-dyna-core`, re-run the agent install command:

```bash
pip install --upgrade ansys-dyna-core
python -m ansys.dyna.core agent --copy
```

## Programmatic access

Locate the instructions from Python:

```python
import ansys.dyna.core
print(ansys.dyna.core.AGENT_INSTRUCTIONS)
# → /path/to/site-packages/ansys/dyna/core/_agent/ansys.dyna.core.md
```

Or print directly:

```bash
python -m ansys.dyna.core agent --print
```

## Manifest tracking

Multiple PyAnsys packages can install agent instructions side-by-side without
conflict. Each registers in `.agent/manifest.json`:

```json
{
  "version": "1.0",
  "packages": [
    {
      "namespace": "ansys.dyna.core",
      "ecosystem": "pypi",
      "package_name": "ansys-dyna-core",
      "mode": "copy",
      "entry_file": "ansys.dyna.core.md",
      "extended_docs": [
        "ansys.dyna.core/deck.md",
        "ansys.dyna.core/keywords.md",
        "ansys.dyna.core/patterns.md"
      ],
      "installed_at": "2026-04-14T00:00:00Z"
    }
  ]
}
```

## When to read what

| Task | Go to |
|------|-------|
| Setting up a new project to use PyDyna | `pydyna_install.md` (this skill) |
| Building a `.k` file with the `keywords` module | PyDyna's `.agent/ansys.dyna.core/keywords.md` |
| Modifying an existing `.k` file (filter / patch) | PyDyna's `.agent/ansys.dyna.core/deck.md` |
| Running the solver from Python | `pydyna_run_api.md` (this skill) |
| Running via `sim run --solver ls_dyna` | This skill's `SKILL.md` (operational protocol) |
| Choosing between SDK vs hand-written `.k` | This skill's `SKILL.md` § Dual-path strategy |
| Post-processing d3plot in Python | PyDyna example: `examples/Taylor_Bar/plot_taylor_bar.html` (DPF) |
