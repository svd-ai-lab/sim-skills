# sim-skills

Per-solver agent skills for the [`sim`](../sim-cli/) simulation runtime. One folder per supported solver. Each folder is a self-contained **skill** in the Anthropic skill format: a top-level `SKILL.md` with YAML frontmatter plus supporting reference docs, workflows, snippets, and tests.

These skills give an LLM agent the **runtime control protocol** for each solver — *not* general API tutoring. They tell the agent how to drive `sim connect / exec / inspect / disconnect` (or `sim run` for one-shot) safely, what inputs to ask for, what to verify, and when to stop.

## Layout

```
sim-skills/
├── README.md            this file (human-facing)
├── CLAUDE.md            AI-facing index + protocol for using these skills
│
├── ansa/                BETA CAE ANSA v25 pre-processor (batch-only)
│   ├── SKILL.md         ← agent protocol with YAML frontmatter
│   ├── known_issues.md
│   ├── reference/       ANSA Python API reference + official docs
│   ├── spec/            Phase 1 design spec
│   ├── docs/            investigation reports
│   ├── tests/           pytest unit + integration
│   ├── skill_tests/     manual protocol acceptance test cases
│   └── pytest.ini
│
├── comsol/              COMSOL Multiphysics via JPype Java API
│   ├── SKILL.md
│   └── workflows/       end-to-end demos (block_with_hole, surface_mount_package)
│
├── flotherm/            Simcenter Flotherm 2504 thermal (GUI + Win32 automation)
│   ├── SKILL.md
│   ├── known_issues.md
│   ├── reference/       runtime patterns, task templates, acceptance checklists
│   ├── docs/            env shell + runtime validation reports
│   ├── tests/           pytest unit + integration
│   ├── skill_tests/     manual protocol test cases
│   ├── workflows/
│   └── pytest.ini
│
├── fluent/              Ansys Fluent via PyFluent (persistent meshing/solver sessions)
│   ├── SKILL.md
│   ├── reference/       PyFluent 0.38 docs, runtime patterns, templates, checklists
│   ├── workflows/       4 end-to-end demos + flipchip_thermal
│   ├── snippets/        13 numbered reusable sim exec snippets
│   ├── tests/           pytest integration
│   ├── skill_tests/     execution + NL test protocols
│   └── LICENSE
│
├── matlab/              MATLAB via sim run (v0 one-shot)
│   ├── SKILL.md
│   ├── driver_upgrade.md   sub-skill for evolving the driver v0→v1
│   ├── reference/
│   ├── workflows/
│   ├── snippets/
│   ├── tests/
│   └── LICENSE
│
└── openfoam/            OpenFOAM v2206 via SSH-tunneled sim serve
    ├── SKILL.md
    ├── reference/       success_patterns + failure_patterns (343 tutorials of evidence)
    ├── docs/            tutorial runner v2, serial + parallel test results
    └── tests/
```

## The 6 skills at a glance

| Skill | Status | Execution model |
|---|---|---|
| **ansa-sim** | Phase 1 | Headless batch (`ansa_win64.exe -execscript -nogui`); no persistent session |
| **comsol-sim** | Working | Persistent session via JPype Java API; GUI client + server topology |
| **flotherm-sim** | Phase A | GUI + Win32 API automation playing back FloSCRIPT XML |
| **fluent-sim** | v0 | Persistent meshing/solver session via PyFluent 0.38 |
| **matlab-sim** | v0 | One-shot `sim run --solver matlab`; persistent session planned for v1 |
| **openfoam-sim** | Working | Persistent session via remote `sim serve` on Linux + SSH tunnel |

## How an agent uses these

For any task:

1. **Identify the solver** from the user's request
2. **Read** the matching `<solver>/SKILL.md` (it has YAML frontmatter telling you exactly when it applies)
3. **Follow the required protocol** in that SKILL.md — input validation, connect, execute, verify, report
4. **Reach for supporting files** when the SKILL.md says to: `reference/` for patterns, `workflows/` for full examples, `snippets/` for ready-made `sim exec` payloads
5. **Never invent solver-specific defaults** for Category A inputs (physical decision inputs) — ask the user

## Runtime requirement

These skills assume the [`sim`](../sim-cli/) runtime is installed (`sim-cli`) and, for skills using persistent sessions, that `sim serve` is running on the machine with the solver license. See the parent project's CLAUDE.md for runtime architecture.

## License

Apache-2.0 (see individual `LICENSE` files where present).
