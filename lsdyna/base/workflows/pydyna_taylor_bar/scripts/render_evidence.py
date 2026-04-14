"""Render Taylor Bar evidence PNGs from d3plot via DPF + PyVista.

Called by run_taylor_bar.ps1 after the solve completes. Runs as a fresh
subprocess so PyVista can use its own off-screen renderer cleanly.

Usage:
    python render_evidence.py <workdir>
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def main(workdir: Path) -> int:
    d3plot = workdir / "d3plot"
    if not d3plot.is_file():
        print(f"ERROR: {d3plot} not found")
        return 1

    evidence_dir = Path(__file__).parent.parent / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Ensure DPF can find ANSYS install
    awp_root = Path("E:/Program Files/ANSYS Inc/v241")
    if awp_root.is_dir() and not os.environ.get("AWP_ROOT241"):
        os.environ["AWP_ROOT241"] = str(awp_root)

    import ansys.dpf.core as dpf

    try:
        dpf.start_local_server(ansys_path=str(awp_root))
    except Exception:
        pass  # Server may already exist

    ds = dpf.DataSources()
    ds.set_result_file_path(str(d3plot), "d3plot")
    model = dpf.Model(ds)

    time_data = model.metadata.time_freq_support.time_frequencies.data_as_list
    print(f"Loaded model: {len(time_data)} states, "
          f"{model.metadata.meshed_region.nodes.n_nodes} nodes, "
          f"{model.metadata.meshed_region.elements.n_elements} elements")

    summary = {
        "n_states": len(time_data),
        "time_start": float(time_data[0]),
        "time_end": float(time_data[-1]),
        "n_nodes": int(model.metadata.meshed_region.nodes.n_nodes),
        "n_elements": int(model.metadata.meshed_region.elements.n_elements),
    }

    # ---- Energy plot via matplotlib ---------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    gke_op = dpf.operators.result.global_kinetic_energy()
    gke_op.inputs.data_sources.connect(ds)
    ke = list(map(float, gke_op.eval().get_field(0).data))

    gie_op = dpf.operators.result.global_internal_energy()
    gie_op.inputs.data_sources.connect(ds)
    ie = list(map(float, gie_op.eval().get_field(0).data))

    te = [k + i for k, i in zip(ke, ie)]

    summary["ke_initial"] = ke[0]
    summary["ke_max"] = max(ke)
    summary["ke_final"] = ke[-1]
    summary["ie_max"] = max(ie)
    summary["ie_final"] = ie[-1]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(time_data, ke, "b-", label="Kinetic Energy", linewidth=2)
    ax.plot(time_data, ie, "r-", label="Internal Energy", linewidth=2)
    ax.plot(time_data, te, "g--", label="Total (KE + IE)", linewidth=1.5, alpha=0.7)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Energy (mJ)")
    ax.set_title("Taylor Bar — Energy Balance via DPF\n"
                 "(KE drops as bar deforms against rigid wall, IE rises)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    energy_png = evidence_dir / "energy_plot.png"
    plt.savefig(energy_png, dpi=100, bbox_inches="tight")
    plt.close()
    print(f"Saved {energy_png}")

    # ---- Stress contour via DPF + PyVista --------------------------------
    import pyvista as pv
    pv.OFF_SCREEN = True

    import numpy as np
    mesh = model.metadata.meshed_region

    disp_op = model.results.displacement.on_last_time_freq()
    disp_field = disp_op.eval().get_field(0)
    disp_arr = np.asarray(disp_field.data).reshape(-1, 3)
    summary["max_disp_mm"] = float(np.linalg.norm(disp_arr, axis=1).max())

    try:
        stress_op = model.results.stress_von_mises.on_last_time_freq()
        stress_field = stress_op.eval().get_field(0)
        stress_data = np.asarray(stress_field.data).flatten()
        summary["stress_vm_max_MPa"] = float(stress_data.max())
        summary["stress_vm_mean_MPa"] = float(stress_data.mean())

        from ansys.dpf.core.plotter import DpfPlotter
        pl = DpfPlotter()
        pl.add_field(stress_field, mesh, deform_by=disp_field, scale_factor=1.0)
        stress_png = evidence_dir / "stress_contour.png"
        pl.show_figure(
            screenshot=str(stress_png),
            show_axes=True,
            window_size=(1600, 1200),
        )
        print(f"Saved {stress_png}")
    except Exception as e:
        print(f"Stress contour failed: {e}")
        # Fallback: deformed mesh only
        stress_png = evidence_dir / "stress_contour.png"
        mesh.plot(
            deformation=disp_field,
            scale_factor=1.0,
            cpos="iso",
            screenshot=str(stress_png),
            background="white",
            show_edges=True,
            color="lightblue",
        )
        print(f"Saved {stress_png} (fallback: deformed mesh only)")

    # ---- Save numerical summary ------------------------------------------
    summary_path = evidence_dir / "physics_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Saved {summary_path}")
    print(json.dumps(summary, indent=2))

    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: render_evidence.py <workdir>")
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))
