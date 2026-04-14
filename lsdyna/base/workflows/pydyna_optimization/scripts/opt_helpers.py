"""Helper functions for plate thickness optimization E2E.

Loaded into the sim session namespace via:
    sim exec "exec(open(r'opt_helpers.py').read())"

After loading, the session namespace gains:
    create_input_deck(thickness)  — return a Deck for given plate thickness
    write_input_deck(thickness, wd) — build deck + write input.k + copy mesh
    run_iteration(thickness, wd)  — full single-thickness pipeline (solve + post)

These functions reference the session-global `kwd`, `Deck`, `run_dyna`, `dpf`,
`workdir`, and `model` set up by the LS-DYNA driver runtime.
"""
import os
import pathlib
import shutil
import pandas as pd
import numpy as np


def create_input_deck(thickness, *, initial_velocity=275.0e2):
    """Build the bar-impact-on-plate deck for the given plate thickness."""
    deck = Deck()
    deck.title = "Bar Thickness - %.4s" % thickness

    # Bar (deformable, hits the plate)
    mat_1 = kwd.Mat003(mid=1)
    mat_1.ro = 7.85e-9
    mat_1.e = 150000.0
    mat_1.pr = 0.34
    mat_1.sigy = 390.0
    mat_1.etan = 90.0

    sec_1 = kwd.SectionSolid(secid=1)
    sec_1.elform = 1

    # Plate (the variable-thickness shell)
    mat_2 = kwd.Mat003(mid=2)
    mat_2.ro = 7.85e-9
    mat_2.e = 1500000.0
    mat_2.pr = 0.34
    mat_2.sigy = 3900.0
    mat_2.etan = 900.0

    sec_2 = kwd.SectionShell(secid=2)
    sec_2.elform = 2
    sec_2.t1 = thickness
    sec_2.t2 = thickness
    sec_2.t3 = thickness
    sec_2.t4 = thickness

    part_1 = kwd.Part()
    part_1.parts = pd.DataFrame({"pid": [1], "mid": [mat_1.mid], "secid": [sec_1.secid]})

    part_2 = kwd.Part()
    part_2.parts = pd.DataFrame({"pid": [2], "mid": [mat_2.mid], "secid": [sec_2.secid]})

    cs_1 = kwd.DefineCoordinateSystem(cid=1)
    cs_1.xl = 1.0
    cs_1.yp = 1.0

    init_vel = kwd.InitialVelocityGeneration()
    init_vel.id = 1
    init_vel.styp = 2
    init_vel.vy = initial_velocity
    init_vel.icid = cs_1.cid

    box_1 = kwd.DefineBox(boxid=1, xmn=-500, xmx=500, ymn=39.0, ymx=40.1, zmn=-500, zmx=500)

    set_node_1 = kwd.SetNodeGeneral()
    set_node_1.sid = 1
    set_node_1.option = "BOX"
    set_node_1.e1 = box_1.boxid

    # Symmetry / fixed BC boxes for the plate
    box_plate_zN = kwd.DefineBox(boxid=2, xmn=-0.1, xmx=10.1, ymn=41.0, ymx=43.0, zmn=-10.1, zmx=-9.9)
    box_plate_zP = kwd.DefineBox(boxid=3, xmn=0.1, xmx=9.9, ymn=41.0, ymx=43.0, zmn=-0.1, zmx=0.1)
    box_plate_xP = kwd.DefineBox(boxid=4, xmn=9.9, xmx=10.1, ymn=41.0, ymx=43.0, zmn=-10.1, zmx=0.1)
    box_plate_xN = kwd.DefineBox(boxid=5, xmn=-0.1, xmx=0.1, ymn=41.0, ymx=43.0, zmn=-9.9, zmx=-0.1)

    set_node_Fixed = kwd.SetNodeGeneral()
    set_node_Fixed.sid = 2
    set_node_Fixed.option = "BOX"
    set_node_Fixed.e1 = box_plate_zN.boxid
    set_node_Fixed.e2 = box_plate_xP.boxid

    fixed_bc = kwd.BoundarySpcSet(dofx=1, dofy=1, dofz=1, dofrx=1, dofry=1, dofrz=1)
    fixed_bc.nsid = set_node_Fixed.sid

    set_node_zNormal = kwd.SetNodeGeneral()
    set_node_zNormal.sid = 3
    set_node_zNormal.option = "BOX"
    set_node_zNormal.e1 = box_plate_zP.boxid

    zNormal_bc = kwd.BoundarySpcSet(dofx=0, dofy=0, dofz=1, dofrx=1, dofry=1, dofrz=0)
    zNormal_bc.nsid = set_node_zNormal.sid

    set_node_xNormal = kwd.SetNodeGeneral()
    set_node_xNormal.sid = 4
    set_node_xNormal.option = "BOX"
    set_node_xNormal.e1 = box_plate_xN.boxid

    xNormal_bc = kwd.BoundarySpcSet(dofx=1, dofy=0, dofz=0, dofrx=0, dofry=1, dofrz=1)
    xNormal_bc.nsid = set_node_xNormal.sid

    box_plate = kwd.DefineBox(boxid=6, xmn=-1, xmx=11, ymn=39.0, ymx=40.1, zmn=-11, zmx=1)
    set_node_plate = kwd.SetNodeGeneral()
    set_node_plate.sid = 5
    set_node_plate.option = "BOX"
    set_node_plate.e1 = box_plate.boxid

    contact = kwd.ContactAutomaticSingleSurface(surfa=0)
    contact.fs = 0.3

    control_term = kwd.ControlTermination(endtim=2.00000e-4, dtmin=0.001)

    deck_dt_out = 8.00000e-8
    deck.extend([
        kwd.DatabaseGlstat(dt=deck_dt_out, binary=3),
        kwd.DatabaseMatsum(dt=deck_dt_out, binary=3),
        kwd.DatabaseNodout(dt=deck_dt_out, binary=3),
        kwd.DatabaseElout(dt=deck_dt_out, binary=3),
        kwd.DatabaseRwforc(dt=deck_dt_out, binary=3),
        kwd.DatabaseBinaryD3Plot(dt=4.00000e-6),
        set_node_1, control_term, contact,
        box_1, box_plate_zN, box_plate_zP, box_plate_xP, box_plate_xN, box_plate,
        set_node_Fixed, set_node_zNormal, set_node_xNormal, set_node_plate,
        fixed_bc, zNormal_bc, xNormal_bc,
        init_vel, cs_1,
        part_1, mat_1, sec_1,
        part_2, mat_2, sec_2,
        kwd.DatabaseHistoryNodeSet(id1=set_node_1.sid),
    ])

    return deck


def write_input_deck(thickness, wd, mesh_filename="bar_impact_mesh.k"):
    """Build a deck, write it + the mesh into wd."""
    deck = create_input_deck(thickness)
    deck.append(kwd.Include(filename=mesh_filename))
    pathlib.Path(wd).mkdir(parents=True, exist_ok=True)
    deck.export_file(os.path.join(wd, "input.k"))
    return deck


def run_iteration(thickness, wd, mesh_src, mesh_filename="bar_impact_mesh.k"):
    """Full single-thickness pipeline: write deck, copy mesh, solve, extract max disp."""
    pathlib.Path(wd).mkdir(parents=True, exist_ok=True)
    if not os.path.isfile(os.path.join(wd, mesh_filename)):
        shutil.copy(mesh_src, os.path.join(wd, mesh_filename))
    write_input_deck(thickness, wd, mesh_filename)
    run_dyna("input.k", working_directory=wd, stream=False)
    if not os.path.isfile(os.path.join(wd, "d3plot")):
        return {"thickness": thickness, "ok": False, "error": "no d3plot"}

    # DPF post: max plate displacement (norm)
    ds = dpf.DataSources()
    ds.set_result_file_path(os.path.join(wd, "d3plot"), "d3plot")
    m = dpf.Model(ds)

    # Get displacement at last state
    disp_op = m.results.displacement.on_last_time_freq()
    disp_field = disp_op.eval().get_field(0)
    disp_arr = np.asarray(disp_field.data).reshape(-1, 3)
    norms = np.linalg.norm(disp_arr, axis=1)

    return {
        "thickness": float(thickness),
        "ok": True,
        "max_disp": float(norms.max()),
        "mean_disp": float(norms.mean()),
        "n_states": len(m.metadata.time_freq_support.time_frequencies.data_as_list),
        "wd": wd,
    }
