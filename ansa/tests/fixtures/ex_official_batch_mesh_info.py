"""EX-13: Official BatchMesh API probe.

Based on BETA CAE's official scripts/Mesh/SampleBatchMesh.py.
The official script uses the batchmesh module for session-based meshing.

We test whether the batchmesh API is importable and functional
without requiring actual geometry or parameter files.
"""
import json
import ansa
from ansa import base, constants

def main():
    deck = constants.NASTRAN
    base.SetCurrentDeck(deck)

    # Test batchmesh module availability (official API)
    bm_available = False
    bm_session_created = False
    try:
        from ansa import batchmesh
        bm_available = True

        # Create a batch mesh session (official pattern from SampleBatchMesh.py)
        session = batchmesh.GetNewSession()
        bm_session_created = session is not None
    except Exception as e:
        bm_error = str(e)

    # Collect parts (empty model = empty list, but API should not error)
    parts = base.CollectEntities(deck, None, "ANSAPART")

    result = {
        "status": "ok",
        "source": "official_batchmesh_api_probe",
        "batchmesh_importable": bm_available,
        "batchmesh_session_created": bm_session_created,
        "ansapart_count": len(parts),
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
