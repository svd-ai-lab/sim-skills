"""Tier 5: LS-DYNA skill structure validation — no solver needed."""
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent


class TestSkillMd:
    def test_skill_md_exists(self):
        assert (SKILL_ROOT / "SKILL.md").is_file()

    def test_skill_md_has_frontmatter(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        assert text.startswith("---")
        assert "name: lsdyna-sim" in text
        assert "description:" in text

    def test_skill_md_has_required_sections(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        assert "Hard constraints" in text
        assert "Required protocol" in text
        assert "File index" in text


class TestBaseReference:
    def test_reference_dir_exists(self):
        assert (SKILL_ROOT / "base" / "reference").is_dir()

    def test_keyword_format_reference(self):
        assert (SKILL_ROOT / "base" / "reference" / "keyword_format.md").is_file()

    def test_material_models_reference(self):
        assert (SKILL_ROOT / "base" / "reference" / "material_models.md").is_file()

    def test_control_cards_reference(self):
        assert (SKILL_ROOT / "base" / "reference" / "control_cards.md").is_file()

    def test_output_files_reference(self):
        assert (SKILL_ROOT / "base" / "reference" / "output_files.md").is_file()

    def test_known_issues_exists(self):
        assert (SKILL_ROOT / "base" / "known_issues.md").is_file()


class TestPyDynaReference:
    def test_pydyna_install_reference(self):
        assert (SKILL_ROOT / "base" / "reference" / "pydyna_install.md").is_file()

    def test_pydyna_keywords_api_reference(self):
        f = SKILL_ROOT / "base" / "reference" / "pydyna_keywords_api.md"
        assert f.is_file()
        text = f.read_text(encoding="utf-8")
        assert "from ansys.dyna.core import Deck" in text
        assert "kwd.Mat003" in text or "kwd.MatElastic" in text

    def test_pydyna_run_api_reference(self):
        f = SKILL_ROOT / "base" / "reference" / "pydyna_run_api.md"
        assert f.is_file()
        text = f.read_text(encoding="utf-8")
        assert "run_dyna" in text

    def test_pydyna_agent_integration_reference(self):
        f = SKILL_ROOT / "base" / "reference" / "pydyna_agent_integration.md"
        assert f.is_file()
        text = f.read_text(encoding="utf-8")
        assert "ansys.dyna.core agent" in text

    def test_session_workflow_reference(self):
        f = SKILL_ROOT / "base" / "reference" / "session_workflow.md"
        assert f.is_file()
        text = f.read_text(encoding="utf-8")
        assert "session.summary" in text
        assert "deck.summary" in text
        assert "results.summary" in text


class TestPyDynaWorkflows:
    def test_taylor_bar_workflow(self):
        f = SKILL_ROOT / "base" / "workflows" / "pydyna_taylor_bar" / "README.md"
        assert f.is_file()

    def test_pendulum_workflow(self):
        assert (SKILL_ROOT / "base" / "workflows" / "pydyna_pendulum" / "README.md").is_file()

    def test_pipe_workflow(self):
        assert (SKILL_ROOT / "base" / "workflows" / "pydyna_pipe" / "README.md").is_file()

    def test_beer_can_workflow(self):
        assert (SKILL_ROOT / "base" / "workflows" / "pydyna_buckling_beer_can" / "README.md").is_file()

    def test_optimization_workflow(self):
        assert (SKILL_ROOT / "base" / "workflows" / "pydyna_optimization" / "README.md").is_file()

    def test_jupyter_plotting_workflow(self):
        assert (SKILL_ROOT / "base" / "workflows" / "pydyna_jupyter_plotting" / "README.md").is_file()


class TestSnippets:
    def test_snippets_dir_exists(self):
        assert (SKILL_ROOT / "base" / "snippets").is_dir()

    def test_single_hex_snippet(self):
        f = SKILL_ROOT / "base" / "snippets" / "01_single_hex_tension.k"
        assert f.is_file()
        text = f.read_text(encoding="utf-8")
        assert "*KEYWORD" in text
        assert "*CONTROL_TERMINATION" in text
        assert "*END" in text


class TestWorkflows:
    def test_workflow_exists(self):
        assert (SKILL_ROOT / "base" / "workflows" / "single_hex_tension").is_dir()

    def test_workflow_readme(self):
        f = SKILL_ROOT / "base" / "workflows" / "single_hex_tension" / "README.md"
        assert f.is_file()
        text = f.read_text(encoding="utf-8")
        assert "7129" in text  # expected cycle count

    def test_evidence_summary(self):
        f = SKILL_ROOT / "base" / "workflows" / "single_hex_tension" / "evidence" / "e2e_summary.json"
        assert f.is_file()
        import json
        data = json.loads(f.read_text(encoding="utf-8"))
        assert data["termination"] == "normal"
        assert data["exit_code"] == 0


class TestSolverLayers:
    def test_solver_14_0_exists(self):
        assert (SKILL_ROOT / "solver" / "14.0" / "notes.md").is_file()

    def test_solver_notes_content(self):
        text = (SKILL_ROOT / "solver" / "14.0" / "notes.md").read_text(encoding="utf-8")
        assert "lsdyna_sp" in text
        assert "AWP_ROOT241" in text
