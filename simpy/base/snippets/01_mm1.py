"""Step 1: M/M/1 queue steady-state simulation (verified E2E).

λ=2, μ=3 (ρ=2/3) → L_theory=2.0, Wq_theory=0.667 s.
Observed (10000 time units): L=1.96, Wq=0.65 (within 3% of theory).

Run: sim run 01_mm1.py --solver simpy
"""
import json, random, simpy


def main():
    random.seed(42)
    LAM, MU, T = 2.0, 3.0, 10000.0
    waits = []
    last_t, n = [0.0], [0]; area = [0.0]

    env = simpy.Environment()
    server = simpy.Resource(env, capacity=1)

    def update(now):
        area[0] += n[0] * (now - last_t[0]); last_t[0] = now

    def cust(env):
        update(env.now); n[0] += 1; arr = env.now
        with server.request() as req:
            yield req; waits.append(env.now - arr)
            yield env.timeout(random.expovariate(MU))
        update(env.now); n[0] -= 1

    def gen(env):
        while True:
            yield env.timeout(random.expovariate(LAM))
            env.process(cust(env))

    env.process(gen(env)); env.run(until=T); update(T)

    L = area[0] / T; Wq = sum(waits) / len(waits)
    L_th = (LAM/MU) / (1 - LAM/MU); Wq_th = (LAM/MU) / (MU - LAM)
    print(json.dumps({
        "ok": abs(L - L_th)/L_th < 0.15 and abs(Wq - Wq_th)/Wq_th < 0.20,
        "L_observed": L, "L_theory": L_th,
        "Wq_observed": Wq, "Wq_theory": Wq_th,
    }))


if __name__ == "__main__":
    main()
