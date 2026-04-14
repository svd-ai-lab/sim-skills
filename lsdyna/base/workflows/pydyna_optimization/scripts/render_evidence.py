"""Optimization sweep evidence renderer.

Walks all `thickness_*` subdirectories under the session workdir,
extracts max plate displacement vs time from each d3plot, and produces
a multi-line plot showing how plate stiffness changes with thickness.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


def main(session_wd: Path) -> int:
    case_dirs = sorted(d for d in session_wd.iterdir() if d.is_dir() and d.name.startswith("thickness_"))
    if not case_dirs:
        print(f"ERROR: no thickness_* dirs in {session_wd}")
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

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    summary = {"runs": [], "session_wd": str(session_wd)}
    fig, ax = plt.subplots(figsize=(10, 6))

    for case_dir in case_dirs:
        m = re.match(r"thickness_(\d+\.\d+)", case_dir.name)
        if not m:
            continue
        thickness = float(m.group(1))

        d3plot = case_dir / "d3plot"
        if not d3plot.is_file():
            print(f"  [skip] {case_dir.name}: no d3plot")
            continue

        ds = dpf.DataSources()
        ds.set_result_file_path(str(d3plot), "d3plot")
        model = dpf.Model(ds)
        time_data = model.metadata.time_freq_support.time_frequencies.data_as_list

        # Track max plate displacement at each state
        max_disp_per_state = []
        for state_idx in range(len(time_data)):
            disp_op = model.results.displacement.on_time_scoping([state_idx + 1])
            disp_field = disp_op.eval().get_field(0)
            arr = np.asarray(disp_field.data).reshape(-1, 3)
            norms = np.linalg.norm(arr, axis=1)
            max_disp_per_state.append(float(norms.max()))

        time_ms = [t * 1000 for t in time_data]
        line = ax.plot(time_ms, max_disp_per_state, label=f"t={thickness:.4f}", linewidth=2)
        peak = max(max_disp_per_state)

        summary["runs"].append({
            "thickness": thickness,
            "n_states": len(time_data),
            "max_disp": peak,
            "case_dir": str(case_dir),
        })
        print(f"  thickness={thickness:.4f}: max_disp={peak:.3f} mm, n_states={len(time_data)}")

    ax.axhline(y=1.0, color="k", linestyle="--", alpha=0.5, label="Target (1.0 mm)")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Max plate displacement (mm)")
    ax.set_title("Plate Thickness Sweep — Max Displacement vs Time\n"
                 "(Thicker plate → less displacement)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    sweep_png = evidence_dir / "thickness_sweep.png"
    plt.savefig(sweep_png, dpi=100, bbox_inches="tight")
    plt.close()
    print(f"Saved {sweep_png}")

    # Render the deformed shape of the best (smallest) and worst (largest) cases
    if len(summary["runs"]) >= 2:
        try:
            import pyvista as pv
            pv.OFF_SCREEN = True

            # Sort by max_disp so we know which is best/worst
            sorted_runs = sorted(summary["runs"], key=lambda r: r["max_disp"])
            for tag, run in [("most_stiff", sorted_runs[0]), ("least_stiff", sorted_runs[-1])]:
                d3plot = Path(run["case_dir"]) / "d3plot"
                ds = dpf.DataSources()
                ds.set_result_file_path(str(d3plot), "d3plot")
                model = dpf.Model(ds)
                mesh = model.metadata.meshed_region
                disp_op = model.results.displacement.on_last_time_freq()
                disp_field = disp_op.eval().get_field(0)
                from ansys.dpf.core.plotter import DpfPlotter
                pl = DpfPlotter()
                pl.add_field(disp_field, mesh, deform_by=disp_field, scale_factor=1.0)
                png = evidence_dir / f"deformed_{tag}_t{run['thickness']:.4f}.png"
                pl.show_figure(
                    screenshot=str(png),
                    show_axes=True,
                    window_size=(1200, 900),
                )
                print(f"Saved {png}  (thickness={run['thickness']:.4f}, max_disp={run['max_disp']:.3f})")
        except Exception as e:
            print(f"Deformed render failed: {e}")

    summary_path = evidence_dir / "physics_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nSaved {summary_path}")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
