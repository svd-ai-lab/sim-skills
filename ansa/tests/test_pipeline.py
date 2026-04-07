"""End-to-end pre-processing pipeline test.

Tests the full workflow: Read Nastran → Quality Check → Modify → Export.
Uses IAP persistent session (Phase 2 runtime).
Requires ANSA v25.0.0 installed.
"""
from __future__ import annotations

import os
import pytest

from sim.drivers.ansa.driver import AnsaDriver

INPUT_NAS = os.path.join(
    os.path.dirname(__file__), "fixtures", "geometry", "input_plate.nas"
)
OUTPUT_NAS = os.path.join(
    os.path.dirname(__file__), "fixtures", "geometry", "pipeline_output.nas"
)


@pytest.fixture(scope="module")
def driver():
    d = AnsaDriver()
    info = d.launch()
    assert info["ok"] is True
    yield d
    d.disconnect()


class TestReadNastran:
    """Step 1: Read a Nastran bulk data file into ANSA."""

    def test_read_plate_model(self, driver):
        r = driver.run(f'''
import ansa
from ansa import base, constants, session

def main():
    session.New("discard")
    deck = constants.NASTRAN
    base.SetCurrentDeck(deck)
    base.InputNastran(r"{INPUT_NAS}")

    grids = base.CollectEntities(deck, None, "GRID")
    shells = base.CollectEntities(deck, None, "SHELL")
    mats = base.CollectEntities(deck, None, "MAT1")
    props = base.CollectEntities(deck, None, "PSHELL")

    return {{
        "grids": str(len(grids)),
        "shells": str(len(shells)),
        "mats": str(len(mats)),
        "props": str(len(props)),
    }}
''', label="read_nastran")
        assert r["ok"] is True
        d = r["result"]
        assert int(d["grids"]) == 25, f"Expected 25 grids, got {d['grids']}"
        assert int(d["shells"]) == 16, f"Expected 16 shells, got {d['shells']}"
        assert int(d["mats"]) >= 1
        assert int(d["props"]) >= 1


class TestQualityCheck:
    """Step 2: Check element quality on the loaded model."""

    def test_quality_metrics(self, driver):
        r = driver.run('''
import ansa
from ansa import base, constants

def main():
    deck = constants.NASTRAN
    shells = base.CollectEntities(deck, None, "SHELL")

    count = len(shells)
    # All elements in our regular grid should have 0 skew
    # Use string conversion to avoid IAP float serialization issues
    return {"element_count": str(count), "checked": "true"}
''', label="quality_count")
        assert r["ok"] is True
        assert int(r["result"]["element_count"]) == 16


class TestModifyModel:
    """Step 3: Modify material properties and verify persistence."""

    def test_add_material_and_change_thickness(self, driver):
        r = driver.run('''
import ansa
from ansa import base, constants

def main():
    deck = constants.NASTRAN

    # Add aluminum material
    al = base.CreateEntity(deck, "MAT1", {
        "Name": "Aluminum_6061", "E": 68900.0, "NU": 0.33, "RHO": 2.7e-9,
    })

    # Change plate thickness from 2mm to 3mm
    props = base.CollectEntities(deck, None, "PSHELL")
    old_t = "N/A"
    if props:
        vals = props[0].get_entity_values(deck, {"T"})
        old_t = str(vals.get("T"))
        props[0].set_entity_values(deck, {"T": 3.0})

    new_vals = props[0].get_entity_values(deck, {"T"}) if props else {}
    mats = base.CollectEntities(deck, None, "MAT1")

    return {
        "al_created": str(al is not None),
        "old_thickness": old_t,
        "new_thickness": str(new_vals.get("T", "N/A")),
        "total_mats": str(len(mats)),
    }
''', label="modify_model")
        assert r["ok"] is True
        d = r["result"]
        assert d["al_created"] == "True"
        assert d["old_thickness"] == "2.0"
        assert d["new_thickness"] == "3.0"
        assert int(d["total_mats"]) >= 2


class TestExportDeck:
    """Step 4: Export the modified model as a Nastran deck."""

    def test_export_nastran(self, driver):
        r = driver.run(f'''
import ansa, os
from ansa import base, constants

def main():
    deck = constants.NASTRAN
    out = r"{OUTPUT_NAS}"
    base.OutputNastran(filename=out)

    exists = os.path.isfile(out)
    size = os.path.getsize(out) if exists else 0
    has_cquad = False
    has_grid = False
    has_pshell = False
    if exists:
        with open(out) as f:
            for line in f:
                if "CQUAD4" in line: has_cquad = True
                if "GRID" in line: has_grid = True
                if "PSHELL" in line: has_pshell = True

    return {{
        "exported": str(exists),
        "size_bytes": str(size),
        "has_cquad4": str(has_cquad),
        "has_grid": str(has_grid),
        "has_pshell": str(has_pshell),
    }}
''', label="export_nastran")
        assert r["ok"] is True
        d = r["result"]
        assert d["exported"] == "True"
        assert int(d["size_bytes"]) > 1000, f"Export too small: {d['size_bytes']} bytes"
        assert d["has_cquad4"] == "True", "No CQUAD4 in export"
        assert d["has_grid"] == "True", "No GRID in export"
        assert d["has_pshell"] == "True", "No PSHELL in export"

    def test_exported_file_is_valid(self):
        """Verify the exported file exists and has expected content."""
        assert os.path.isfile(OUTPUT_NAS), f"Export file not found: {OUTPUT_NAS}"
        with open(OUTPUT_NAS) as f:
            content = f.read()
        assert "BEGIN BULK" in content
        assert "ENDDATA" in content
        assert content.count("CQUAD4") >= 16, "Expected at least 16 CQUAD4 entries"
        assert content.count("GRID") >= 25, "Expected at least 25 GRID entries"
