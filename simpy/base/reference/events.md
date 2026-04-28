# Events

## timeout

```python
yield env.timeout(5)            # advance simulation clock by 5
yield env.timeout(2, value='x') # also returns 'x' as event value
```

## process (sub-process completion)

```python
sub = env.process(other(env))
result = yield sub              # waits for `other` to finish
```

## event (one-shot)

```python
e = env.event()
def trigger(env, e):
    yield env.timeout(5)
    e.succeed('payload')
env.process(trigger(env, e))
val = yield e                   # waits, returns 'payload'
```

## Combining: all_of / any_of

```python
e1 = env.timeout(3)
e2 = env.timeout(5)

# wait for both
results = yield env.all_of([e1, e2])    # at t=5
# wait for first
done = yield env.any_of([e1, e2])       # at t=3
```

## Interrupts

```python
def worker(env):
    try:
        yield env.timeout(10)
        print('finished')
    except simpy.Interrupt as i:
        print(f'interrupted: {i.cause}')

p = env.process(worker(env))

def killer(env, p):
    yield env.timeout(5)
    p.interrupt('boss called')

env.process(killer(env, p))
env.run()
```
