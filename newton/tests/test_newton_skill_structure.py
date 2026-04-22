"""Structural assertions for the newton skill bundle.

Guarantees the SKILL.md + reference + workflow files that the skill's
frontmatter advertises actually exist. Lightweight — no newton import.
"""
from __future__ import annotations

from pathlib import Path

import pytest

HERE = Path(__file__).parent.parent


@pytest.fixture(scope="module")
def skill_root() -> Path:
    return HERE


def test_skill_md_exists(skill_root):
    p = skill_root / "SKILL.md"
    assert p.exists(), f"missing {p}"
    text = p.read_text(encoding="utf-8")
    assert text.startswith("---"), "SKILL.md must begin with YAML frontmatter"
    assert "newton-sim" in text


@pytest.mark.parametrize("name", [
    "recipe_schema.md",
    "solvers.md",
    "two_routes.md",
    "cli_mapping.md",
])
def test_reference_doc_exists(skill_root, name):
    p = skill_root / "base" / "reference" / name
    assert p.exists(), f"missing {p}"
    assert p.stat().st_size > 200


@pytest.mark.parametrize("workflow,artifact", [
    ("basic_pendulum", "recipe.json"),
    ("robot_g1", "recipe.json"),
    ("cable_twist", "script.py"),
])
def test_workflow_artifact_exists(skill_root, workflow, artifact):
    wf = skill_root / "base" / "workflows" / workflow
    assert (wf / artifact).exists(), f"missing {wf / artifact}"
    assert (wf / "README.md").exists(), f"missing README for {workflow}"


def test_solver_1x_notes(skill_root):
    p = skill_root / "solver" / "1_x" / "notes.md"
    assert p.exists(), f"missing {p}"
    text = p.read_text(encoding="utf-8")
    assert "NEWTON_VENV" in text
