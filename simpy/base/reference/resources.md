# SimPy resources

| Class | Capacity | Use for |
|---|---|---|
| `Resource` | finite servers | gas pumps, doctors, machines |
| `PriorityResource` | finite + priority queue | priority customers |
| `PreemptiveResource` | finite + preemption | preemptable jobs |
| `Container` | continuous level | tank, fuel, materials |
| `Store` | item buffer | parts on a conveyor |
| `FilterStore` | item buffer + filter | dispatch by type |

## Resource

```python
server = simpy.Resource(env, capacity=2)        # 2 parallel servers
with server.request() as req:
    yield req                                    # wait
    yield env.timeout(service_time)              # use
# released automatically on exit of `with`
```

## Container

```python
tank = simpy.Container(env, capacity=1000, init=500)
yield tank.put(50)                               # add 50
yield tank.get(30)                               # remove 30
print(tank.level)                                # 520
```

## Store

```python
buf = simpy.Store(env, capacity=10)
yield buf.put({'id': 1, 'kind': 'A'})
item = yield buf.get()
```

## FilterStore

```python
fs = simpy.FilterStore(env)
yield fs.put({'kind': 'A'})
a_item = yield fs.get(lambda x: x['kind'] == 'A')
```
