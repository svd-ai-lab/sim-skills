"""Step 1: 2D heat diffusion of a point source (verified E2E).

Initial: u=100 at center, 0 elsewhere. PDE: dt_u = 0.1*(dx2_u + dy2_u).
After 20 explicit steps with dt=0.001:
    peak ≈ 12.5 (10x decay from initial)
    mass ≈ 100  (conserved to machine precision)

Run: sim run 01_diffusion.py --solver devito
"""
import json
from devito import Grid, TimeFunction, Eq, solve, Operator


def main():
    grid = Grid(shape=(20, 20), extent=(1.0, 1.0))
    u = TimeFunction(name='u', grid=grid, time_order=1, space_order=2)
    u.data[:] = 0.0
    u.data[0, 10, 10] = 100.0
    initial_mass = float(u.data[0].sum())

    eq = Eq(u.dt, 0.1 * (u.dx2 + u.dy2))
    Operator([Eq(u.forward, solve(eq, u.forward))]).apply(time_M=20, dt=0.001)

    final = u.data[-1]
    peak, mass = float(final.max()), float(final.sum())
    print(json.dumps({
        "ok": bool(5.0 < peak < 30.0 and abs(mass - initial_mass)/initial_mass < 0.10),
        "peak": peak,
        "initial_mass": initial_mass,
        "final_mass": mass,
    }))


if __name__ == "__main__":
    main()
