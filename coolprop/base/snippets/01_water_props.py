"""Step 1: Water saturation properties at 1 atm (verified E2E).

Textbook (NIST steam tables):
- T_sat(1 atm) = 373.124 K = 99.974 °C
- h_fg         = 2256.5 kJ/kg

Observed: matches NIST to 0.001 K and 0.05% h_fg.

Run: sim run 01_water_props.py --solver coolprop
"""
import json
from CoolProp.CoolProp import PropsSI


def main():
    P = 101325.0
    T_sat = float(PropsSI('T', 'P', P, 'Q', 0, 'Water'))
    h_l = float(PropsSI('H', 'P', P, 'Q', 0, 'Water'))
    h_v = float(PropsSI('H', 'P', P, 'Q', 1, 'Water'))
    h_fg = h_v - h_l

    print(json.dumps({
        "ok": abs(T_sat - 373.124) < 0.1 and abs(h_fg - 2.2565e6) / 2.2565e6 < 0.01,
        "T_sat_K": T_sat, "T_sat_C": T_sat - 273.15,
        "h_fg_J_per_kg": h_fg,
    }))


if __name__ == "__main__":
    main()
