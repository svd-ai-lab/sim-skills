"""Beer Can buckling evidence renderer."""
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

    awp_root = Path("E:/Program Files/ANSYS Inc/v241")
    if awp_root.is_dir() and not os.environ.get("AWP_ROOT241"):
        os.environ["AWP_ROOT241"] = str(awp_root)

    import ansys.dpf.core as dpf
    try:
        dpf.start_local_server(ansys_path=str(awp_root))
    except Exception:
        pass

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

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    # Energy plot
    gke_op = dpf.operators.result.global_kinetic_energy()
    gke_op.inputs.data_sources.connect(ds)
    ke = list(map(float, gke_op.eval().get_field(0).data))
    gie_op = dpf.operators.result.global_internal_energy()
    gie_op.inputs.data_sources.connect(ds)
    ie = list(map(float, gie_op.eval().get_field(0).data))

    summary["ke_max"] = max(ke)
    summary["ie_max"] = max(ie)
    summary["ie_final"] = ie[-1]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(time_data, ke, "b-", label="Kinetic Energy", linewidth=2)
    ax.plot(time_data, ie, "r-", label="Internal Energy (work done by load)", linewidth=2)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Energy")
    ax.set_title("Beer Can Buckling — Energy History\n"
                 "(Implicit nonlinear; IE rise tracks compression work)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    energy_png = evidence_dir / "energy_plot.png"
    plt.savefig(energy_png, dpi=100, bbox_inches="tight")
    plt.close()
    print(f"Saved {energy_png}")

    # Force-displacement curve (if SPC forces available)
    try:
        # Get displacement of a load node over time (e.g. node 50 = first load node)
        all_disp_z = []
        for state_idx in range(len(time_data)):
            disp_op = model.results.displacement.on_time_scoping([state_idx + 1])
            disp_field = disp_op.eval().get_field(0)
            arr = np.asarray(disp_field.data).reshape(-1, 3)
            all_disp_z.append(arr[:, 2])  # Z direction = compression axis

        # Track max compression (most negative Z displacement)
        z_extreme = [d.min() for d in all_disp_z]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(time_data, z_extreme, "purple", linewidth=2)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Most-compressed node — Z displacement (in)")
        ax.set_title("Beer Can — Top Compression Over Time\n"
                     "(Snap-down indicates buckling event)")
        ax.grid(True, alpha=0.3)
        compr_png = evidence_dir / "compression_curve.png"
        plt.savefig(compr_png, dpi=100, bbox_inches="tight")
        plt.close()
        print(f"Saved {compr_png}")
        summary["max_compression"] = float(min(z_extreme))
    except Exception as e:
        print(f"Compression curve failed: {e}")

    # Final deformed shape with stress
    try:
        import pyvista as pv
        pv.OFF_SCREEN = True

        mesh = model.metadata.meshed_region
        disp_op = model.results.displacement.on_last_time_freq()
        disp_field = disp_op.eval().get_field(0)
        disp_arr = np.asarray(disp_field.data).reshape(-1, 3)
        summary["max_disp"] = float(np.linalg.norm(disp_arr, axis=1).max())

        try:
            stress_op = model.results.stress_von_mises.on_last_time_freq()
            stress_field = stress_op.eval().get_field(0)
            stress_data = np.asarray(stress_field.data).flatten()
            summary["stress_vm_max"] = float(stress_data.max())

            from ansys.dpf.core.plotter import DpfPlotter
            pl = DpfPlotter()
            pl.add_field(stress_field, mesh, deform_by=disp_field, scale_factor=1.0)
            buckled_png = evidence_dir / "buckled_can.png"
            pl.show_figure(
                screenshot=str(buckled_png),
                show_axes=True,
                window_size=(1600, 1200),
            )
            print(f"Saved {buckled_png}")
        except Exception as e:
            print(f"Stress contour failed: {e}, falling back to deformed mesh")
            buckled_png = evidence_dir / "buckled_can.png"
            mesh.plot(
                deformation=disp_field,
                scale_factor=1.0,
                cpos="iso",
                screenshot=str(buckled_png),
                background="white",
                show_edges=True,
                color="lightblue",
            )
            print(f"Saved {buckled_png} (fallback)")
    except Exception as e:
        print(f"Final shape render failed: {e}")

    summary_path = evidence_dir / "physics_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nSaved {summary_path}")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
