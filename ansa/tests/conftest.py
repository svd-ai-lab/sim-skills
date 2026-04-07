"""Shared fixtures and skip logic for ANSA tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "sim" / "src"))

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ANSA_ROOT = Path(r"E:\Program Files (x86)\ANSA")
ANSA_BAT = ANSA_ROOT / "ansa_v25.0.0" / "ansa64.bat"
FIXTURES = Path(__file__).parent / "fixtures"

# ---------------------------------------------------------------------------
# Skip helpers
# ---------------------------------------------------------------------------
_ansa_installed: bool | None = None


def _check_ansa() -> bool:
    global _ansa_installed
    if _ansa_installed is None:
        _ansa_installed = ANSA_BAT.is_file()
    return _ansa_installed


_skip_no_ansa = pytest.mark.skipif(
    not _check_ansa(),
    reason="ANSA not installed or ansa64.bat not found",
)

# ---------------------------------------------------------------------------
# Markers
# ---------------------------------------------------------------------------


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "slow: marks tests that run ANSA (slow)")
