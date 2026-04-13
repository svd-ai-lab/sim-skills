"""Tier 5: CFX skill structure validation — no solver needed."""
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent


class TestSkillMd:
    def test_skill_md_exists(self):
        assert (SKILL_ROOT / "SKILL.md").is_file()

    def test_skill_md_has_frontmatter(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        assert text.startswith("---")
        assert "name: cfx-sim" in text
        assert "description:" in text

    def test_skill_md_has_required_sections(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        assert "Hard constraints" in text
        assert "Required protocol" in text
        assert "File index" in text


class TestBaseReference:
    def test_reference_dir_exists(self):
        assert (SKILL_ROOT / "base" / "reference").is_dir()

    def test_ccl_language_reference(self):
        assert (SKILL_ROOT / "base" / "reference" / "ccl_language.md").is_file()

    def test_cli_tools_reference(self):
        assert (SKILL_ROOT / "base" / "reference" / "cli_tools.md").is_file()

    def test_boundary_conditions_reference(self):
        assert (SKILL_ROOT / "base" / "reference" / "boundary_conditions.md").is_file()

    def test_solver_control_reference(self):
        assert (SKILL_ROOT / "base" / "reference" / "solver_control.md").is_file()

    def test_post_processing_reference(self):
        assert (SKILL_ROOT / "base" / "reference" / "post_processing.md").is_file()

    def test_session_workflow_reference(self):
        f = SKILL_ROOT / "base" / "reference" / "session_workflow.md"
        assert f.is_file()
        text = f.read_text(encoding="utf-8")
        assert "hybrid" in text.lower()
        assert "evaluate" in text
        assert "chr(64)" in text
        assert "enterccl" in text

    def test_known_issues_exists(self):
        assert (SKILL_ROOT / "base" / "known_issues.md").is_file()


class TestSnippets:
    def test_snippets_dir_exists(self):
        assert (SKILL_ROOT / "base" / "snippets").is_dir()

    def test_smoke_test_snippet(self):
        f = SKILL_ROOT / "base" / "snippets" / "01_smoke_test.ccl"
        assert f.is_file()
        text = f.read_text(encoding="utf-8")
        assert "Maximum Number of Iterations" in text

    def test_post_session_snippet(self):
        f = SKILL_ROOT / "base" / "snippets" / "04_post_pressure.cse"
        assert f.is_file()
        text = f.read_text(encoding="utf-8")
        assert "Colour Variable" in text
        assert ">print" in text


class TestWorkflows:
    def test_vmfl015_workflow_exists(self):
        assert (SKILL_ROOT / "base" / "workflows" / "vmfl015").is_dir()

    def test_vmfl015_readme(self):
        f = SKILL_ROOT / "base" / "workflows" / "vmfl015" / "README.md"
        assert f.is_file()
        text = f.read_text(encoding="utf-8")
        assert "VMFL015" in text
        assert "122" in text  # iteration count

    def test_vmfl015_evidence_images(self):
        evidence = SKILL_ROOT / "base" / "workflows" / "vmfl015" / "evidence"
        assert evidence.is_dir()
        assert (evidence / "pressure_contour.png").is_file()
        assert (evidence / "velocity_contour.png").is_file()
        assert (evidence / "e2e_summary.json").is_file()

    def test_vmfl015_session_transcript(self):
        transcript = SKILL_ROOT / "base" / "workflows" / "vmfl015" / "evidence" / "session_e2e_transcript.json"
        assert transcript.is_file()
        import json
        data = json.loads(transcript.read_text(encoding="utf-8"))
        assert len(data) >= 15  # at least 15 steps
        assert all(step["result"].get("ok", True) for step in data)


class TestSolverLayers:
    def test_solver_24_1_exists(self):
        assert (SKILL_ROOT / "solver" / "24.1" / "notes.md").is_file()

    def test_solver_notes_content(self):
        text = (SKILL_ROOT / "solver" / "24.1" / "notes.md").read_text(encoding="utf-8")
        assert "cfx5solve" in text
        assert "AWP_ROOT241" in text
