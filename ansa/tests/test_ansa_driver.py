"""Unit tests for the ANSA driver.

All tests in TestDetect, TestLint, TestConnect (mocked), TestParseOutput,
and TestErrorPaths run WITHOUT ANSA installed.

TestExecution requires a real ANSA installation and is marked @slow.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "sim" / "src"))

from sim.drivers.ansa.driver import AnsaDriver, _find_installation
from conftest import FIXTURES, _skip_no_ansa


@pytest.fixture
def driver():
    return AnsaDriver()


# ── TestPreFlight ────────────────────────────────────────────────────────────


class TestPreFlight:
    def test_driver_importable(self):
        from sim.drivers.ansa import AnsaDriver
        assert AnsaDriver is not None

    def test_driver_name(self, driver):
        assert driver.name == "ansa"

    @_skip_no_ansa
    def test_connect_status_ok(self, driver):
        info = driver.connect()
        assert info.status == "ok"

    @_skip_no_ansa
    def test_connect_version(self, driver):
        info = driver.connect()
        assert info.version == "25.0.0"

    @_skip_no_ansa
    def test_connect_message_has_bat_path(self, driver):
        info = driver.connect()
        assert "ansa64.bat" in info.message


# ── TestDetect ───────────────────────────────────────────────────────────────


class TestDetect:
    def test_good_ansa_script(self, driver):
        assert driver.detect(FIXTURES / "good_ansa_script.py") is True

    def test_no_import(self, driver):
        assert driver.detect(FIXTURES / "no_import.py") is False

    def test_no_main(self, driver):
        assert driver.detect(FIXTURES / "no_main.py") is True

    def test_gui_script(self, driver):
        assert driver.detect(FIXTURES / "gui_script.py") is True

    def test_syntax_error_still_detected(self, driver):
        # detect uses regex on raw text, not AST — syntax errors don't block detection
        assert driver.detect(FIXTURES / "syntax_error.py") is True

    def test_nonexistent_file(self, driver):
        assert driver.detect(Path("/nonexistent/file.py")) is False

    def test_txt_file(self, driver, tmp_path):
        f = tmp_path / "readme.txt"
        f.write_text("not an ansa script")
        assert driver.detect(f) is False


# ── TestLint ─────────────────────────────────────────────────────────────────


class TestLint:
    def test_good_script_ok(self, driver):
        r = driver.lint(FIXTURES / "good_ansa_script.py")
        assert r.ok is True
        assert len(r.diagnostics) == 0

    def test_no_import_fails(self, driver):
        r = driver.lint(FIXTURES / "no_import.py")
        assert r.ok is False
        assert any("import ansa" in d.message for d in r.diagnostics)

    def test_syntax_error_fails(self, driver):
        r = driver.lint(FIXTURES / "syntax_error.py")
        assert r.ok is False
        assert any("Syntax error" in d.message for d in r.diagnostics)

    def test_no_main_warns(self, driver):
        r = driver.lint(FIXTURES / "no_main.py")
        assert r.ok is True
        assert any("main()" in d.message for d in r.diagnostics)

    def test_gui_functions_warn(self, driver):
        r = driver.lint(FIXTURES / "gui_script.py")
        assert r.ok is True
        assert any("GUI" in d.message for d in r.diagnostics)

    def test_empty_file(self, driver, tmp_path):
        f = tmp_path / "empty.py"
        f.write_text("")
        r = driver.lint(f)
        assert r.ok is False

    def test_ansa_db_nonexistent(self, driver):
        r = driver.lint(Path("/nonexistent.ansa"))
        assert r.ok is False

    def test_ansa_db_empty(self, driver, tmp_path):
        f = tmp_path / "empty.ansa"
        f.write_bytes(b"")
        r = driver.lint(f)
        assert r.ok is False

    def test_ansa_db_nonempty(self, driver, tmp_path):
        f = tmp_path / "model.ansa"
        f.write_bytes(b"\x00" * 100)
        r = driver.lint(f)
        assert r.ok is True

    def test_unsupported_extension(self, driver, tmp_path):
        f = tmp_path / "model.stl"
        f.write_text("solid test")
        r = driver.lint(f)
        assert r.ok is False


# ── TestParseOutput ──────────────────────────────────────────────────────────


class TestParseOutput:
    def test_empty(self, driver):
        assert driver.parse_output("") == {}

    def test_no_json(self, driver):
        assert driver.parse_output("hello world\nno json here") == {}

    def test_simple_json(self, driver):
        assert driver.parse_output('{"count": 42}') == {"count": 42}

    def test_last_json_wins(self, driver):
        stdout = 'line1\n{"a": 1}\nline3\n{"b": 2}'
        assert driver.parse_output(stdout) == {"b": 2}

    def test_invalid_json_skipped(self, driver):
        stdout = '{invalid\n{"valid": true}'
        assert driver.parse_output(stdout) == {"valid": True}


# ── TestErrorPaths ───────────────────────────────────────────────────────────


class TestErrorPaths:
    def test_run_file_not_installed(self, driver, monkeypatch):
        import sim.drivers.ansa.driver as drv
        monkeypatch.setattr(drv, "_find_installation", lambda: None)
        with pytest.raises(RuntimeError, match="ANSA"):
            driver.run_file(FIXTURES / "good_ansa_script.py")

    def test_run_ansa_db_raises(self, driver, tmp_path):
        f = tmp_path / "model.ansa"
        f.write_bytes(b"\x00" * 100)
        # Even with installation, .ansa files can't be "run"
        # (but we need a fake installation to get past the first check)
        import sim.drivers.ansa.driver as drv
        orig = drv._find_installation

        def fake_install():
            return ("fake.bat", "fake.exe", "25.0.0")

        drv._find_installation = fake_install
        try:
            with pytest.raises(RuntimeError, match="Cannot directly execute"):
                driver.run_file(f)
        finally:
            drv._find_installation = orig

    def test_unsupported_extension(self, driver, tmp_path):
        f = tmp_path / "model.stl"
        f.write_text("solid test")
        import sim.drivers.ansa.driver as drv
        orig = drv._find_installation
        drv._find_installation = lambda: ("fake.bat", "fake.exe", "25.0.0")
        try:
            with pytest.raises(RuntimeError, match="Unsupported file type"):
                driver.run_file(f)
        finally:
            drv._find_installation = orig


# ── TestExecution (real ANSA required) ───────────────────────────────────────


class TestExecution:
    @_skip_no_ansa
    @pytest.mark.slow
    def test_run_file_returns_result(self, driver):
        result = driver.run_file(FIXTURES / "good_ansa_script.py")
        assert hasattr(result, "exit_code")
        assert hasattr(result, "stdout")
        assert hasattr(result, "duration_s")
        assert result.solver == "ansa"
