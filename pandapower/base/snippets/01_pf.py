"""Step 1: 2-bus power flow (verified E2E).

Slack b1 (20 kV) — 10 km NAYY 4x150 SE line — load b2 (0.5 MW).
Acceptance: vm_pu(b2) ∈ [0.95, 1.0] (small voltage drop).
Observed: vm_pu(b2) = 0.998, losses = 1.4 kW.

Run: sim run 01_pf.py --solver pandapower
"""
import json
import pandapower as pp


def main():
    net = pp.create_empty_network()
    b1, b2 = pp.create_bus(net, vn_kv=20.0), pp.create_bus(net, vn_kv=20.0)
    pp.create_ext_grid(net, b1)
    pp.create_line(net, b1, b2, length_km=10, std_type='NAYY 4x150 SE')
    pp.create_load(net, b2, p_mw=0.5)
    pp.runpp(net)
    vm = float(net.res_bus.vm_pu[b2])
    losses = float(net.res_line.pl_mw.sum())
    print(json.dumps({
        "ok": 0.95 <= vm <= 1.0 and 0 < losses < 0.01,
        "vm_pu_b2": vm,
        "loss_mw": losses,
    }))


if __name__ == "__main__":
    main()
