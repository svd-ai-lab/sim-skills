"""Smallest end-to-end PyBaMM run: SPM, default parameters, 1 hour discharge."""
import pybamm

model = pybamm.lithium_ion.SPM()
sim = pybamm.Simulation(model)
sim.solve([0, 3600])  # solve from t=0 to t=3600 s

solution = sim.solution
voltage = solution["Voltage [V]"].entries
time_s = solution["Time [s]"].entries
print(f"final voltage: {voltage[-1]:.3f} V at t={time_s[-1]:.0f} s")
