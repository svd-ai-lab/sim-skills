"""Step 1: Adiabatic flame T for stoichiometric CH4/air (verified E2E).

Mechanism: gri30 (53 species).
State: 300 K, 1 atm, CH4:O2:N2 = 1:2:7.52.
Process: equilibrate('HP').

Textbook: ~2225 K. Observed: 2225.5 K.

Run: sim run 01_adiabatic_flame.py --solver cantera
"""
import json
import cantera as ct


def main():
    g = ct.Solution('gri30.yaml')
    g.TPX = 300.0, ct.one_atm, 'CH4:1, O2:2, N2:7.52'
    g.equilibrate('HP')
    print(json.dumps({
        "ok": abs(g.T - 2225.0) < 30.0,
        "T_ad_K": float(g.T),
        "X_CO2": float(g['CO2'].X[0]),
        "X_H2O": float(g['H2O'].X[0]),
    }))


if __name__ == "__main__":
    main()
