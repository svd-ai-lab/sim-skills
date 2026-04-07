<div align="center">

<img src="assets/banner.svg" alt="sim-skills — teach your agent to drive every engineering tool" width="820">

<br>

**Teach your agent to drive every engineering tool.**

*[`sim-cli`](https://github.com/svd-ai-lab/sim-cli) opens the door.*
*`sim-skills` walks the agent through it.*

<p align="center">
  <a href="#-the-skill-grid"><img src="https://img.shields.io/badge/Skills-growing_library-8b5cf6?style=for-the-badge" alt="Skills library"></a>
  <a href="https://github.com/svd-ai-lab/sim-cli"><img src="https://img.shields.io/badge/Runtime-sim--cli-3b82f6?style=for-the-badge" alt="sim-cli runtime"></a>
  <a href="#-how-an-agent-uses-a-skill"><img src="https://img.shields.io/badge/Format-Anthropic_Skill-22c55e?style=for-the-badge" alt="Anthropic skill format"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-eab308?style=for-the-badge" alt="License"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/category-agent_playbooks-blueviolet" alt="Category">
  <img src="https://img.shields.io/badge/one_folder-per_solver-cbd5e1" alt="One folder per solver">
  <img src="https://img.shields.io/badge/pairs_with-sim--cli-3776AB" alt="Pairs with sim-cli">
  <img src="https://img.shields.io/badge/status-alpha-f97316" alt="Status: alpha">
</p>

[The Skill Grid](#-the-skill-grid) · [Why](#-why-sim-skills) · [How to use](#-how-an-agent-uses-a-skill) · [Conventions](#-cross-skill-conventions) · [Runtime](#-runtime-dependency) · [sim-cli →](https://github.com/svd-ai-lab/sim-cli)

</div>

---

## 📰 News

- **2026-04-07** 🚀 **sim-skills v0.1** — first public release on GitHub. Six skills in the grid, consolidated from the earlier `svd-ai-lab/ion-agent-{ansa,comsol,flotherm,fluent,matlab,openfoam}` family. Every skill now ships in the standard Anthropic skill format (YAML frontmatter + `SKILL.md`).
- **2026-04-07** 🤝 Paired with the companion runtime [`sim-cli`](https://github.com/svd-ai-lab/sim-cli) — the two repos are designed to grow in lockstep, one skill per new driver.

---

## 🤔 Why sim-skills?

LLM agents already know how to write PyFluent, MATLAB, COMSOL, and OpenFOAM scripts — training data is full of them. What they *don't* have is **operational discipline** for each tool: which inputs are physical decisions vs. operational defaults, what the acceptance criterion actually is, when to stop and ask, which API version's quirks bite where.

Writing the same discipline into every agent prompt from scratch is how teams burn weeks and waste compute. `sim-skills` is the missing library:

- **One folder per solver.** Each folder is a self-contained Anthropic-format skill — `SKILL.md` with YAML frontmatter, plus `reference/`, `workflows/`, `snippets/`, `tests/` as the SKILL.md points to them.
- **Runtime control, not API tutoring.** The skills tell the agent how to drive `sim connect / exec / inspect / disconnect` safely — they assume the agent already knows the solver's own API, and teach it the *operational* layer around that.
- **Cross-skill conventions baked in.** Input classification (Category A/B/C), acceptance-criterion rules, and escalation triggers live in [`CLAUDE.md`](CLAUDE.md) so every skill obeys the same protocol.
- **Paired with [`sim-cli`](https://github.com/svd-ai-lab/sim-cli).** The runtime provides the transport; the skills provide the playbook. Neither works well alone.

> Think of it this way: `sim-cli` is the ignition and the steering wheel. `sim-skills` is the driving school.

---

## 🧭 The Skill Grid

Every skill lives in its own top-level folder. The grid is **open and growing** — add a new skill by dropping a `<solver>/SKILL.md` in and registering it in [`CLAUDE.md`](CLAUDE.md). Current contents of `main`:

| Skill | Domain | Execution model | Phase | What it's for |
|---|---|---|---|---|
| [**fluent-sim**](fluent/SKILL.md) | CFD | Persistent meshing / solver session (PyFluent 0.38) | v0 ✅ | Incremental `sim exec` snippets or single-file workflows against a live Fluent session |
| [**comsol-sim**](comsol/SKILL.md) | Multiphysics | Persistent JPype Java API session | Working ✅ | Long multiphysics runs with optional human GUI oversight |
| [**openfoam-sim**](openfoam/SKILL.md) | CFD (OSS) | Remote `sim serve` on Linux via SSH tunnel | Working ✅ | Meshing, MPI parallel, classifier-based pass/fail on OpenFOAM v2206 |
| [**ansa-sim**](ansa/SKILL.md) | Structural pre-processing | Headless batch (`ansa_win64 -execscript -nogui`) | Phase 1 🟡 | BETA CAE ANSA v25 scripts; no persistent session yet |
| [**flotherm-sim**](flotherm/SKILL.md) | Electronics thermal | GUI + Win32 FloSCRIPT playback | Phase A 🟡 | Simcenter Flotherm 2504 `.pack` cases |
| [**matlab-sim**](matlab/SKILL.md) | Numerical / scripting | One-shot `sim run --solver matlab` | v0 🟡 | `.m` scripts one-shot; persistent session planned for v1 |
| **+ your skill** | — | — | 🛠 | Drop a `<solver>/SKILL.md`, register in `CLAUDE.md`, open a PR |

**Legend** · ✅ Working · 🟡 In progress (phased rollout) · 🛠 Open for contribution

---

## 🎯 How an agent uses a skill

When a task involves a supported solver, the agent follows the same five steps for every skill:

1. **Identify the solver** from the user's request
2. **Read** `<solver>/SKILL.md` — its YAML `description` says exactly when the skill applies, and the body has the required protocol
3. **Follow the protocol**: input validation → connect → execute → verify → report
4. **Reach for supporting files** when SKILL.md tells it to:
   - `reference/` — patterns, templates, API docs
   - `workflows/` — end-to-end example cases
   - `snippets/` — ready-made `sim exec` payloads
   - `skill_tests/` — manual acceptance test cases
5. **Never invent solver-specific defaults** for Category A inputs (physical decisions) — ask the user

The human workflow is even simpler: an engineer points the LLM at `sim-skills`, names the solver, and the agent knows what to do next.

---

## 📏 Cross-skill conventions

These apply to every skill in the grid. Details live in [`CLAUDE.md`](CLAUDE.md); the summary:

| Convention | One-line rule |
|---|---|
| **Category A inputs** | Physical decisions (geometry, materials, BCs, acceptance criteria). **Ask the user** if absent — pressure to "just use defaults" does NOT override this. |
| **Category B inputs** | Operational defaults (processors, ui_mode, smoke-test iterations). May default; must disclose. |
| **Category C inputs** | File-derivable (cell zones, surface names, solver version). Infer via a diagnostic snippet, not from reference examples. |
| **Acceptance criteria** | `exit_code == 0` is **not** sufficient. Every task needs an outcome-based criterion (outlet temp in 28–35 °C, min mesh quality > 0.2, etc.). |
| **Reference examples ≠ defaults** | Values in `<skill>/reference/examples/` describe a specific published test case. Offer them, never silently adopt them. |
| **When to stop** | Solver fails to launch, snippet raises or returns `ok=false`, session state drifts from expectation, acceptance cannot be verified → report, don't silently retry. |

---

## 🔌 Runtime dependency

These skills are useless without the [`sim-cli`](https://github.com/svd-ai-lab/sim-cli) runtime. The runtime provides:

- `sim connect / exec / inspect / disconnect` for persistent solver sessions
- `sim run` for one-shot scripts
- `sim lint`, `sim logs`, `sim ps` for the operational layer around both

For each solver there is a matching driver at `sim-cli/src/sim/drivers/<solver>/`. The skill in this repo is the agent-facing protocol; the driver is the Python-facing implementation. Neither works well alone.

```bash
# Install the runtime (has all seven drivers available today):
uv pip install "git+https://github.com/svd-ai-lab/sim-cli.git"

# Then point your LLM agent at this repo and let it read the SKILL.md files.
```

---

## 📂 Repo layout

```
sim-skills/
├── README.md          this file (human-facing)
├── CLAUDE.md          AI-facing index, protocol, cross-skill conventions
├── LICENSE            Apache-2.0
│
├── fluent/            Ansys Fluent via PyFluent (persistent sessions)
├── comsol/            COMSOL Multiphysics via JPype Java API
├── openfoam/          OpenFOAM v2206 via SSH-tunneled sim serve
├── ansa/              BETA CAE ANSA v25 pre-processor (batch, Phase 1)
├── flotherm/          Simcenter Flotherm 2504 (GUI + Win32, Phase A)
├── matlab/            MATLAB via sim run (v0 one-shot)
│
└── assets/            banner and related graphics
```

Each `<solver>/` directory is self-contained: `SKILL.md` at the top is the agent entry point; the rest (`reference/`, `workflows/`, `snippets/`, `tests/`, `skill_tests/`, `docs/`) is supporting material the SKILL.md links to as needed. Folder shapes vary by skill and by phase — Fluent and Flotherm are the most built-out today.

---

## 🔗 Related projects

- **[`sim-cli`](https://github.com/svd-ai-lab/sim-cli)** — the paired runtime. One CLI, one HTTP protocol, an open driver registry. This repo is its agent-facing twin.

---

## 📄 License

Apache-2.0 — see [LICENSE](LICENSE). Individual skills may ship their own `LICENSE` file (all Apache-2.0 today).
