"""Geometry-to-mesh pipeline test.

Tests the full CAD pre-processing workflow:
  STEP geometry → surface mesh → quality check → material assignment → Nastran export

Uses OpenCASCADE screw.step (89KB, 10 faces) as input.
Requires ANSA v25.0.0 installed.
"""
from __future__ import annotations

import os
import pytest

from sim.drivers.ansa.driver import AnsaDriver

STEP_FILE = os.path.join(
    os.path.dirname(__file__), "fixtures", "geometry", "screw.step"
)
OUTPUT_NAS = os.path.join(
    os.path.dirname(__file__), "fixtures", "geometry", "screw_test_output.nas"
)


@pytest.fixture(scope="module")
def driver():
    d = AnsaDriver()
    info = d.launch()
    assert info["ok"] is True
    yield d
    d.disconnect()


class TestLoadSTEP:
    """Step 1: Import STEP CAD geometry."""

    def test_load_step_geometry(self, driver):
        r = driver.run(f'''
import ansa
from ansa import base, constants, session

def main():
    session.New("discard")
    deck = constants.NASTRAN
    base.SetCurrentDeck(deck)
    base.Open(r"{STEP_FILE}")

    faces = base.CollectEntities(deck, None, "FACE")
    parts = base.CollectEntities(deck, None, "ANSAPART")
    return {{"faces": str(len(faces)), "parts": str(len(parts))}}
''', label="load_step")
        assert r["ok"] is True
        assert int(r["result"]["faces"]) >= 5, f"Expected >=5 faces, got {r['result']['faces']}"
        assert int(r["result"]["parts"]) >= 1


class TestMeshGeneration:
    """Step 2: Generate surface mesh from CAD faces."""

    def test_mesh_faces(self, driver):
        r = driver.run('''
import ansa
from ansa import base, constants, mesh

def main():
    deck = constants.NASTRAN
    faces = base.CollectEntities(deck, None, "FACE")

    # Set finer mesh target length before meshing
    try:
        base.SetANSAdefaultsValues({"element_length": "1.0"})
    except:
        pass

    ret = mesh.Mesh(faces)

    shells = base.CollectEntities(deck, None, "SHELL")
    grids = base.CollectEntities(deck, None, "GRID")
    return {
        "mesh_ret": str(ret),
        "shells": str(len(shells)),
        "grids": str(len(grids)),
    }
''', label="mesh_generation")
        assert r["ok"] is True
        assert r["result"]["mesh_ret"] == "1", "mesh.Mesh() should return 1 on success"
        shells = int(r["result"]["shells"])
        grids = int(r["result"]["grids"])
        assert shells > 10, f"Expected >10 shell elements, got {shells}"
        assert grids > 10, f"Expected >10 grid nodes, got {grids}"


class TestQualityCheck:
    """Step 3: Verify mesh quality."""

    def test_zero_off_elements(self, driver):
        r = driver.run('''
import ansa
from ansa import base, constants

def main():
    deck = constants.NASTRAN
    shells = base.CollectEntities(deck, None, "SHELL")
    props = base.CollectEntities(deck, None, "__PROPERTIES__")

    total_off = 0
    for p in props:
        try:
            off = base.CalculateOffElements(p)
            total_off += off.get("TOTAL OFF", 0)
        except:
            pass

    return {"shells": str(len(shells)), "total_off": str(total_off)}
''', label="quality_check")
        assert r["ok"] is True
        assert int(r["result"]["total_off"]) == 0, \
            f"Expected 0 off-elements, got {r['result']['total_off']}"


class TestMaterialAssignment:
    """Step 4: Add engineering material."""

    def test_create_material(self, driver):
        r = driver.run('''
import ansa
from ansa import base, constants

def main():
    deck = constants.NASTRAN
    mat = base.CreateEntity(deck, "MAT1", {
        "Name": "Steel_4140", "E": 210000.0, "NU": 0.3, "RHO": 7.85e-9,
    })
    mats = base.CollectEntities(deck, None, "MAT1")
    return {"created": str(mat is not None), "total_mats": str(len(mats))}
''', label="add_material")
        assert r["ok"] is True
        assert r["result"]["created"] == "True"


class TestExportNastran:
    """Step 5: Export meshed model as Nastran solver deck."""

    def test_export(self, driver):
        r = driver.run(f'''
import ansa, os
from ansa import base, constants

def main():
    deck = constants.NASTRAN
    out = r"{OUTPUT_NAS}"
    base.OutputNastran(filename=out)
    exists = os.path.isfile(out)
    size = os.path.getsize(out) if exists else 0
    return {{"exported": str(exists), "size_bytes": str(size)}}
''', label="export_nastran")
        assert r["ok"] is True
        assert r["result"]["exported"] == "True"
        assert int(r["result"]["size_bytes"]) > 1000, \
            f"Export too small: {r['result']['size_bytes']} bytes"

    def test_exported_file_valid(self):
        assert os.path.isfile(OUTPUT_NAS)
        with open(OUTPUT_NAS) as f:
            content = f.read()
        assert "BEGIN BULK" in content
        assert "GRID" in content
        grid_count = content.count("GRID")
        assert grid_count > 10, f"Expected >10 GRID entries, got {grid_count}"
