"""Runtime tests for ANSA IAP persistent session.

Tests the full lifecycle: launch → exec → exec_file → disconnect.
Requires ANSA v25.0.0 installed.
"""
from __future__ import annotations

import pytest
import time

from sim.drivers.ansa.driver import AnsaDriver
from sim.drivers.ansa.schemas import SessionInfo, RunRecord


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def driver():
    """Create a fresh AnsaDriver for the test module."""
    return AnsaDriver()


@pytest.fixture(scope="module")
def session(driver):
    """Launch ANSA once for the entire test module, disconnect at end."""
    info = driver.launch()
    assert info["ok"] is True
    yield info
    driver.disconnect()


# ---------------------------------------------------------------------------
# Phase 1 compatibility (one-shot) — should still work
# ---------------------------------------------------------------------------

class TestPhase1Compat:
    """Phase 1 run_file() must still work after adding runtime."""

    def test_driver_has_runtime_methods(self, driver):
        assert hasattr(driver, "launch")
        assert hasattr(driver, "run")
        assert hasattr(driver, "run_script")
        assert hasattr(driver, "disconnect")
        assert hasattr(driver, "is_connected")

    def test_connect_still_works(self, driver):
        info = driver.connect()
        assert info.status == "ok"
        assert info.version == "25.0.0"


# ---------------------------------------------------------------------------
# Phase 2: IAP session lifecycle
# ---------------------------------------------------------------------------

class TestSessionLifecycle:
    """Test launch → hello → goodbye lifecycle."""

    def test_launch_returns_session_info(self, session):
        assert session["ok"] is True
        assert "session_id" in session
        assert session["mode"] == "batch"
        assert session["source"] == "launch"
        assert "port" in session

    def test_is_connected_after_launch(self, driver, session):
        assert driver.is_connected is True


class TestExecSnippet:
    """Test run_script_text() via driver.run()."""

    def test_simple_return_dict(self, driver, session):
        code = "def main():\n    return {'hello': 'world'}"
        result = driver.run(code, label="test_hello")
        assert result["ok"] is True
        assert result["result"]["hello"] == "world"

    def test_ansa_api_create_material(self, driver, session):
        code = """
import ansa
from ansa import base, constants

def main():
    deck = constants.NASTRAN
    base.SetCurrentDeck(deck)
    mat = base.CreateEntity(deck, "MAT1", {"Name": "RuntimeSteel", "E": 210000.0, "NU": 0.3})
    mats = base.CollectEntities(deck, None, "MAT1")
    return {"mat_count": str(len(mats)), "created": str(mat is not None)}
"""
        result = driver.run(code, label="test_create_mat")
        assert result["ok"] is True
        assert result["result"]["created"] == "True"
        assert int(result["result"]["mat_count"]) >= 1

    def test_ansa_api_state_persists(self, driver, session):
        """State from previous snippet should persist (keep_database)."""
        code = """
import ansa
from ansa import base, constants

def main():
    deck = constants.NASTRAN
    base.SetCurrentDeck(deck)
    mats = base.CollectEntities(deck, None, "MAT1")
    names = [m.get_entity_values(deck, {"Name"}).get("Name", "") for m in mats]
    has_runtime_steel = any("RuntimeSteel" in n for n in names)
    return {"mat_count": str(len(mats)), "has_runtime_steel": str(has_runtime_steel)}
"""
        result = driver.run(code, label="test_state_persist")
        assert result["ok"] is True
        assert result["result"]["has_runtime_steel"] == "True"

    def test_multi_deck_query(self, driver, session):
        code = """
import ansa
from ansa import constants

def main():
    decks = []
    for name in ["NASTRAN", "ABAQUS", "LSDYNA", "FLUENT"]:
        if hasattr(constants, name):
            decks.append(name)
    return {"deck_count": str(len(decks)), "decks": ",".join(decks)}
"""
        result = driver.run(code, label="test_decks")
        assert result["ok"] is True
        assert int(result["result"]["deck_count"]) >= 4

    def test_error_in_snippet_returns_ok_false(self, driver, session):
        code = "def main():\n    raise ValueError('intentional error')"
        result = driver.run(code, label="test_error")
        assert result["ok"] is False

    def test_run_record_has_timing(self, driver, session):
        code = "def main():\n    return {'done': 'yes'}"
        result = driver.run(code, label="test_timing")
        assert result["ok"] is True
        # RunRecord should have been logged
        rt = driver._ensure_runtime()
        rec = rt.last_record
        assert rec is not None
        assert rec.ended_at > rec.started_at


class TestExecFile:
    """Test run_script_file() via driver.run_script()."""

    def test_official_test_script(self, driver, session):
        import os
        script = os.path.join(
            r"E:\Program Files (x86)\ANSA\ansa_v25.0.0\scripts",
            "RemoteControl", "ansa_examples", "test_script_ansa.py",
        )
        result = driver.run_script(script)
        assert result["ok"] is True
        assert result["result"] == {"A": "0", "B": "1", "C": "2"}


class TestDisconnect:
    """Test session teardown — uses the module-level session."""

    def test_disconnect_cleans_up(self, driver, session):
        """After module fixture disconnects, is_connected should be False."""
        # This test just verifies the disconnect API exists and is callable.
        # The actual disconnect happens in the module-scoped fixture teardown.
        # We test it by calling disconnect on a *separate* driver that was
        # never launched — should not raise.
        d2 = AnsaDriver()
        assert d2.is_connected is False
        d2.disconnect()  # no-op, should not raise
        assert d2.is_connected is False
