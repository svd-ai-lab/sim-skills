<div align="center">

<img src="assets/banner.svg" alt="sim-skills - teach your agent to drive engineering tools" width="820">

<br>

**Teach your agent to drive engineering tools through sim.**

*[`sim-runtime`](https://github.com/svd-ai-lab/sim-cli) provides the runtime.*
*`sim-skills` provides the agent playbooks.*

<p align="center">
  <a href="#-current-skills"><img src="https://img.shields.io/badge/Skills-lean_core-8b5cf6?style=for-the-badge" alt="Skills library"></a>
  <a href="https://github.com/svd-ai-lab/sim-plugin-index"><img src="https://img.shields.io/badge/Drivers-plugin_repos-3b82f6?style=for-the-badge" alt="Plugin repositories"></a>
  <a href="#-how-this-repo-fits-the-plugin-model"><img src="https://img.shields.io/badge/Model-runtime_plus_plugins-22c55e?style=for-the-badge" alt="Runtime plus plugins"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-eab308?style=for-the-badge" alt="License"></a>
</p>

[Current Skills](#-current-skills) . [Plugin Model](#-how-this-repo-fits-the-plugin-model) . [How Agents Use Skills](#-how-an-agent-uses-a-skill) . [Conventions](#-cross-skill-conventions) . [Runtime](#-runtime-dependency)

</div>

---

## Why sim-skills?

LLM agents can often write solver scripts, but they still need operational discipline: which inputs are physical decisions, what counts as acceptance, when to inspect runtime state, when to stop, and which logs or artifacts prove the run actually worked.

`sim-skills` is the shared playbook layer for that discipline. It is intentionally smaller now that solver drivers have moved into individual plugin repositories.

- **Core agent protocols live here.** The shared `sim-cli` skill owns lifecycle, command surface, version probing, input classification, acceptance, and escalation.
- **Open-source skills can live here.** Lightweight solver or library skills that do not require private/vendor assets may remain in this repo.
- **Driver implementations live in plugins.** Runtime driver code ships through out-of-tree plugin packages and the plugin index.
- **Plugin-specific skills travel with plugins.** When a driver needs specialized workflows, private references, GUI automation, or vendor-specific troubleshooting, keep that skill content with the matching plugin repo.

---

## How this repo fits the plugin model

The sim ecosystem is split deliberately:

| Layer | Repo | Audience | Contents |
|---|---|---|---|
| Runtime | [`sim-cli`](https://github.com/svd-ai-lab/sim-cli) | Users and plugin authors | `sim-runtime`, CLI commands, HTTP protocol, plugin loading |
| Plugin registry | [`sim-plugin-index`](https://github.com/svd-ai-lab/sim-plugin-index) | Users and installers | Curated plugin metadata for `sim plugin list / install` |
| Plugin repos | `sim-plugin-<name>` | Driver maintainers | Driver code, tests, packaged plugin metadata, plugin-owned skills |
| Shared skills | This repo | Agents and contributors | Shared runtime skill plus open/public agent playbooks |

This repo should not mirror every plugin. If a driver has been extracted to a plugin repository, keep the implementation and driver-specific agent playbook there. Link to the plugin registry from here instead of carrying stale copies.

---

## Current skills

Current tracked skill folders on `main`:

| Skill | Domain | Execution model | Status | Notes |
|---|---|---|---|---|
| [**sim-cli**](sim-cli/SKILL.md) | Shared runtime contract | Persistent sessions and one-shot runs | Core | Load alongside any solver or plugin skill. Owns lifecycle, command surface, Step-0 version probe, input classification, acceptance, and escalation. |
| [**sim-cli/gui**](sim-cli/gui/SKILL.md) | Runtime-injected GUI tool | GUI-capable sessions | Core | Shared actuation API for drivers that expose a `gui` object through `sim exec`. |
| [**openfoam-sim**](openfoam/SKILL.md) | Open-source CFD | Case files, command-line runs, remote Linux workflows | Active | OpenFOAM case setup, solver selection, mesh/log diagnosis, parallel execution, and post-processing guidance. |
| [**ltspice-sim**](ltspice/SKILL.md) | Circuit simulation | One-shot batch runs | Active | Netlist authoring, platform dispatch, `.meas` result extraction, and log-based acceptance. |
| [**coolprop-sim**](coolprop/SKILL.md) | Thermophysical properties | One-shot Python scripts | Active | Property lookups for fluids, humid air, saturation curves, and cycle-analysis tasks. |

Extracted or private drivers are intentionally not listed as local folders here. Discover installable drivers through:

```bash
uv pip install sim-runtime
sim plugin list
sim plugin install <name>
```

---

## How an agent uses a skill

When a task involves sim, the agent should:

1. Read [`sim-cli/SKILL.md`](sim-cli/SKILL.md) for the runtime contract.
2. Read the solver or plugin-specific `SKILL.md`.
3. Run the required Step-0 probe before choosing version-specific guidance.
4. Classify missing inputs before inventing defaults.
5. Execute through `sim connect`, `sim exec`, `sim inspect`, `sim run`, and related runtime commands as appropriate.
6. Verify outcome-based acceptance, not just `exit_code == 0`.

For plugin-owned skills, the plugin repo is the source of truth. Do not recreate driver-specific instructions here unless they are genuinely shared across multiple drivers.

---

## Cross-skill conventions

These apply to every driver skill, whether the skill lives here or inside a plugin repo. The canonical source is [`sim-cli/`](sim-cli/SKILL.md).

| Convention | One-line rule | Full reference |
|---|---|---|
| **Category A inputs** | Physical decisions require the user or a task spec. | [input_classification.md](sim-cli/reference/input_classification.md) |
| **Category B inputs** | Operational defaults may be chosen, but must be disclosed. | [input_classification.md](sim-cli/reference/input_classification.md) |
| **Category C inputs** | File-derivable facts should be inferred from diagnostics. | [input_classification.md](sim-cli/reference/input_classification.md) |
| **Acceptance criteria** | A successful process exit is not enough. | [acceptance.md](sim-cli/reference/acceptance.md) |
| **Step-0 version probe** | Inspect runtime versions before loading version-specific guidance. | [version_awareness.md](sim-cli/reference/version_awareness.md) |
| **Escalation** | Report launch failures, runtime drift, snippet failures, and failed acceptance directly. | [escalation.md](sim-cli/reference/escalation.md) |

---

## Runtime dependency

These skills are designed for the [`sim-runtime`](https://github.com/svd-ai-lab/sim-cli) CLI and plugin system.

```bash
# Install the solver-agnostic runtime.
uv pip install sim-runtime

# Discover and install driver plugins.
sim plugin list
sim plugin install <name>

# Then point your agent at the relevant SKILL.md files.
```

The runtime provides transport and process control. Plugins provide driver implementations. Skills provide the agent-facing protocol for using both without drifting into ad hoc automation.

---

## Repo layout

```text
sim-skills/
├── README.md          Human-facing overview
├── CLAUDE.md          Contributor guide for editing this repo
├── LICENSE            Apache-2.0
├── NOTICE
├── assets/            Banner and related graphics
├── sim-cli/           Shared runtime contract and runtime-injected tool skills
├── openfoam/          OpenFOAM agent playbook
├── ltspice/           LTspice agent playbook
└── coolprop/          CoolProp agent playbook
```

Ignored local folders such as `.local/`, `.claude/`, or local vendor/reference caches are not part of the public skill grid.

---

## Related projects

- **[`sim-cli`](https://github.com/svd-ai-lab/sim-cli)** - runtime, CLI, protocol, and plugin loading.
- **[`sim-plugin-index`](https://github.com/svd-ai-lab/sim-plugin-index)** - curated registry for installable driver plugins.
- **`sim-plugin-<name>` repos** - driver-specific implementations, tests, plugin metadata, and plugin-owned skills.

---

## License

Apache-2.0 - see [LICENSE](LICENSE). Plugin repositories may carry their own notices and licensing constraints.
