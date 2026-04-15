# SimPy workflow

```python
import simpy
import random

random.seed(42)

# 1. Create environment (== simulation clock + scheduler)
env = simpy.Environment()

# 2. Define processes (generator functions)
def customer(env, server, name):
    arrival = env.now
    with server.request() as req:
        yield req                                # wait for resource
        wait = env.now - arrival
        service_time = random.expovariate(1/3.0) # 3 s mean
        yield env.timeout(service_time)
    print(f'{name} done, wait={wait:.2f}')

# 3. Define an arrival generator
def gen(env, server, mean_iat=2.0):
    i = 0
    while True:
        yield env.timeout(random.expovariate(1/mean_iat))
        i += 1
        env.process(customer(env, server, f'c{i}'))

# 4. Create resources
server = simpy.Resource(env, capacity=1)

# 5. Schedule top-level process
env.process(gen(env, server))

# 6. Run
env.run(until=1000)

# 7. Read out (whatever you tracked)
```

## Always emit JSON

```python
import json
print(json.dumps({
    "ok": True,
    "now": env.now,
    "n_customers": i,
    "avg_wait_s": sum(waits)/len(waits),
}))
```
